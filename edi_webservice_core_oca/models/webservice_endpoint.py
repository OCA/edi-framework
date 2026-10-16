# Copyright 2026 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class WebserviceEndpoint(models.Model):
    _inherit = "webservice.endpoint"

    exchange_type_ids = fields.One2many(
        comodel_name="edi.exchange.type",
        inverse_name="webservice_endpoint_id",
        string="Exchange Types",
    )
    exchange_type_count = fields.Integer(
        compute="_compute_exchange_type_count",
    )

    @api.depends("exchange_type_ids")
    def _compute_exchange_type_count(self):
        for rec in self:
            rec.exchange_type_count = len(rec.exchange_type_ids)

    def action_view_exchange_types(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Exchange Types"),
            "res_model": "edi.exchange.type",
            "view_mode": "list,form",
            "domain": [("webservice_endpoint_id", "=", self.id)],
        }
