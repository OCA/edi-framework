# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    origin_edi_endpoint_id = fields.Many2one(
        string="EDI origin endpoint",
        comodel_name="edi.endpoint",
        ondelete="set null",
        related="origin_exchange_record_id.edi_endpoint_id",
        store=True,
    )
