# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    edi_account_move_out_exchange_type_id = fields.Many2one(
        string="EDI Exchange type for outgoing invoices",
        comodel_name="edi.exchange.type",
        help="If defined, this EDI Exchange Type will be used to export invoices "
        "of that customer.",
    )
