# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class EDIExchangeType(models.Model):
    _inherit = "edi.exchange.type"

    webservice_backend_id = fields.Many2one(
        related="backend_id.webservice_backend_id",
    )
    webservice_send_enabled = fields.Boolean(
        compute="_compute_webservice_send_enabled",
        help="Technical flag: whether `send_model_id` inherits from the "
        "webservice send handler (`edi.webservice.send`), directly or via "
        "a custom extension. Used to show/hide webservice-specific "
        "settings on this type.",
    )
    webservice_endpoint_id = fields.Many2one(
        "webservice.endpoint",
        string="WebService Endpoint",
        help="Webservice endpoint to call when sending through this "
        "exchange type (see `edi.webservice.send`). Extra call "
        "parameters can still be provided via the advanced YAML settings.",
    )
    webservice_send_as_bytes = fields.Boolean(
        string="Send As Bytes",
        help="By sending as bytes, `requests` won't try to guess and/or "
        "alter the encoding of the file being sent.",
    )

    @api.depends("send_model_id")
    def _compute_webservice_send_enabled(self):
        registry = self.env.registry
        handler_cls = registry["edi.webservice.send"]
        for rec in self:
            model_name = rec.send_model_id.model
            rec.webservice_send_enabled = bool(
                model_name
                and model_name in registry
                and issubclass(registry[model_name], handler_cls)
            )
