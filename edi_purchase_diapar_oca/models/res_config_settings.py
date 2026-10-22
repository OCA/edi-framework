from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    edi_receipt_qty_policy = fields.Selection(
        related="company_id.edi_receipt_qty_policy", readonly=False
    )
