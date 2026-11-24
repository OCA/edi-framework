from odoo import models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_supplier_code_or_ean(self, seller_id):
        self.ensure_one()
        code, origin_code = "", ""
        seller_line = self.seller_ids.filtered(
            lambda seller: seller.partner_id.id == seller_id and seller.product_code
        )
        if seller_line and seller_line[0].product_code:
            code = seller_line[0].product_code
            origin_code = "supplier"
        elif self.barcode:
            code = self.barcode
            origin_code = "barcode"
        if not code:
            raise ValidationError(self.env._("No code for this product %s!", self.name))
        return code, origin_code
