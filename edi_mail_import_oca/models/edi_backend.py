# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import ast

from odoo import models


class EdiBackend(models.Model):
    _name = "edi.backend"
    _inherit = ["edi.backend", "mail.alias.mixin"]

    def _alias_get_creation_values(self):
        values = super()._alias_get_creation_values()
        values["alias_model_id"] = self.env["ir.model"]._get("edi.exchange.record").id
        if self.id:
            values["alias_defaults"] = defaults = ast.literal_eval(
                self.alias_defaults or "{}"
            )
            defaults["backend_id"] = self.id
        return values

    def _mail_exchange_type_pending_input_domain(self):
        """Domain for retrieving input exchange types for emails."""
        return [
            ("backend_type_id", "=", self.backend_type_id.id),
            ("direction", "=", "input"),
            "|",
            ("backend_id", "=", False),
            ("backend_id", "=", self.id),
            ("mail_record_policy", "!=", False),
        ]
