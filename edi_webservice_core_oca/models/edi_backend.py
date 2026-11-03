# Copyright 2020 Dixmit
# Copyright 2026 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EdiBackend(models.Model):
    _inherit = "edi.backend"

    webservice_backend_id = fields.Many2one("webservice.backend")
    webservice_endpoint_count = fields.Integer(
        related="webservice_backend_id.endpoint_count"
    )
    webservice_endpoint_ids = fields.One2many(
        related="webservice_backend_id.endpoint_ids",
        readonly=True,
        string="Webservice endpoints",
    )

    def action_manage_webservice_endpoints(self):
        """Open the endpoints of the linked webservice backend.

        Same action as the webservice backend's own endpoints button.
        """
        self.ensure_one()
        return self.webservice_backend_id.action_view_endpoints()
