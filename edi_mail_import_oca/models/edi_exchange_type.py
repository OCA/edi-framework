# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EdiExchangeType(models.Model):
    _inherit = "edi.exchange.type"

    mail_record_policy = fields.Selection(
        [
            ("full", "Only archive the full mail message"),
            ("pattern", "Match single filename pattern"),
        ]
    )
