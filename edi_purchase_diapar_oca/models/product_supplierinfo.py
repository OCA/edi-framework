from odoo import api, models
from odoo.exceptions import ValidationError


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.model
    def compute_edi_partner(self, partner):
        """
        :param partner: purchase order/invoice supplier
        :return: EDI supplier used
        """
        edi_exchange_type_obj = self.env["edi.exchange.type"]
        exchange_type = edi_exchange_type_obj.search(
            [("partner_ids", "=", partner.id)], limit=1
        )
        if not exchange_type:
            raise ValidationError(
                self.env._("No EDI Exchange Type for this supplier %s!") % partner.name
            )
        if partner.edi_purchase_supplier_id:
            return partner.edi_purchase_supplier_id
        else:
            return partner

    def _get_price_field(self):
        return "price"

    @api.model
    def update_purchase_price(self, vals):
        """
        Looks for most recent price on purchase table of prices, only for
        EDI suppliers
        :param vals:
        :return: updated values with product price
        """
        supplier_id = vals.get("partner_id", False)
        supplier = self.env["res.partner"].browse(supplier_id)
        if supplier.is_edi:
            edi_supplier = self.compute_edi_partner(supplier)
            supplier_code = vals.get("product_code", False)
            if not supplier_code:
                raise ValidationError(
                    self.env._("Please give a supplier code to create the product!")
                )
            price = self.env["supplier.price.list"].search(
                [
                    ("supplier_id", "=", edi_supplier.id),
                    ("supplier_code", "=", supplier_code),
                ],
                order="apply_date DESC",
            )
            if price:
                price_field = self._get_price_field()
                vals.update({price_field: price[0].price})
                price.sudo().write({"price_updated": True})
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals = self.update_purchase_price(vals)
        return super().create(vals_list)

    @api.constrains("product_code", "partner_id")
    def _check_product_code(self):
        if self.product_code and self.partner_id.is_edi:
            if not self.product_code.isdigit():
                raise ValidationError(
                    self.env._(
                        "Product code must be numeric for %s!", self.partner_id.name
                    )
                ) from None
            if len(self.product_code) != 6:
                raise ValidationError(
                    self.env._(
                        "Product code must be 6 digits for %s!", self.partner_id.name
                    )
                ) from None
