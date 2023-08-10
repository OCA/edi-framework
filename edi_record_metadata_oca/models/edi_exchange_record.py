# Copyright 2023 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import json

from odoo import api, fields, models

from ..fields import BetterSerialized


class EDIExchangeRecord(models.Model):

    _inherit = "edi.exchange.record"

    metadata = BetterSerialized(
        help="JSON-like metadata used for technical purposes.",
        default={},
    )
    metadata_display = fields.Text(
        compute="_compute_metadata_display",
        help="Enable debug mode to be able to inspect data.",
    )

    @api.depends("metadata")
    def _compute_metadata_display(self):
        for rec in self:
            rec.metadata_display = json.dumps(rec.metadata, sort_keys=True, indent=4)

    def set_metadata(self, data):
        self.metadata = data

    def get_metadata(self):
        return self.metadata
