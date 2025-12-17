from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    edi_purchase_supplier_id = fields.Many2one(
        "res.partner",
        domain=[("supplier_rank", ">", 0), ("is_edi", "=", True)],
    )
    is_edi = fields.Boolean(string="Is an EDI supplier")
    show_discount = fields.Boolean()
