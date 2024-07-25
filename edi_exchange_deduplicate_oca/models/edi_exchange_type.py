# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EDIExchangeType(models.Model):

    _inherit = "edi.exchange.type"

    deduplicate_on_send = fields.Boolean(
        string="Deduplicate on Send",
        default=False,
        help="Before sending an exchange record, check if a fresher one does not "
        "exist for same record; if so, mark oldest one as obsolete.",
    )
    delete_obsolete_records = fields.Boolean(
        string="Delete obsolete records",
        default=True,
        help="Delete records marked as obsolete.",
    )
