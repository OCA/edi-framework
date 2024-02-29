# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EDIExchangeRecord(models.Model):
    _inherit = "edi.exchange.record"

    storage_id = fields.Many2one(
        comodel_name="fs.storage",
        readonly=True,
        string="FS Storage",
        help="Record created from a file found in this FS storage",
    )
