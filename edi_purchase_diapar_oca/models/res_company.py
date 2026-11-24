from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    edi_receipt_qty_policy = fields.Selection(
        selection=[
            ("ordered", "From PO"),
            ("received_file", "From EDI Receipt File"),
        ],
        string="Receipt Quantity Policy",
        default="ordered",
        help="Policy to determine the quantity to be used in "
        "receipt when processing EDI file for purchase order.",
    )
