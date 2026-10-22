# Copyright (C) 2016-Today: Druidoo (<http://www.druidoo.net/>)
# @author: Druidoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import api, fields, models


class SupplierPriceList(models.Model):
    _name = "supplier.price.list"
    _description = "Supplier Price List"

    import_date = fields.Date(readonly=True)
    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="EDI Supplier",
        domain=[("is_edi", "=", True), ("supplier_rank", ">", 0)],
        readonly=True,
        required=True,
    )
    product_tmpl_id = fields.Many2one(
        comodel_name="product.template", string="Product", ondelete="set null"
    )
    product_name = fields.Char(readonly=True, required=True)
    supplier_code = fields.Char(readonly=True, required=True)
    price = fields.Float(
        digits="Product Price",
        readonly=True,
        required=True,
        help="The price HT to purchase a product",
    )
    apply_date = fields.Date(readonly=True, required=True)
    barcode = fields.Char(string="Ean")
    price_updated = fields.Boolean()

    def _get_price_field(self):
        return "price"

    def _create_supplierinfo_with_price(self, vals):
        price_field = self._get_price_field()
        vals.update({price_field: self.price})
        return self.env["product.supplierinfo"].create(vals)

    def button_create_product(self):
        self.ensure_one()
        # create new product
        product_tmpl_id = self.env["product.template"].create(
            {
                "name": self.product_name,
                "sale_ok": True,
                "purchase_ok": True,
                "type": "consu",
                "default_code": self.supplier_code,
                "barcode": self.barcode,
            }
        )
        # link product with current supplier price list
        self.sudo().product_tmpl_id = product_tmpl_id.id
        # create product supplier info
        self._create_supplierinfo_with_price(
            {
                "partner_id": self.supplier_id.id,
                "product_code": self.supplier_code,
                "product_tmpl_id": product_tmpl_id.id,
            }
        )
        self.sudo().price_updated = True
        # find similar supplier price list
        supplier_price_list_ids = self.search(
            [
                ("supplier_id", "=", self.supplier_id.id),
                ("product_name", "=", self.product_name),
                ("supplier_code", "=", self.supplier_code),
                ("product_tmpl_id", "=", False),
            ]
        )
        # link product to similar supplier price list
        supplier_price_list_ids.sudo().write({"product_tmpl_id": product_tmpl_id.id})
        # create action to open newly created product form view
        action = {
            "name": self.env._("Product Form"),
            "res_model": "product.template",
            "type": "ir.actions.act_window",
            "target": "current",
            "res_id": product_tmpl_id.id,
        }
        return action

    @api.model
    def update_product_price_list(self, product, splists):
        splists = splists.sorted("apply_date")
        splist = splists[-1]
        price = splist.price
        args = [
            ("product_code", "=", splist.supplier_code),
            ("product_tmpl_id", "=", product.id),
        ]
        supplierinfos = self.env["product.supplierinfo"].search(args, limit=1)
        if supplierinfos:
            price_field = self._get_price_field()
            if getattr(supplierinfos, price_field) != price:
                supplierinfos.write(
                    {
                        price_field: price,
                    }
                )
        else:
            self._create_supplierinfo_with_price(
                {
                    "partner_id": splist.supplier_id.id,
                    "product_code": splist.supplier_code,
                    "product_tmpl_id": product.id,
                }
            )
        splists.sudo().write({"price_updated": True})
