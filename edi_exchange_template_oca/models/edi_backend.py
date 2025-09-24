# Copyright 2020 ACSONE SA
# Copyright 2025 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class EDIBackend(models.Model):
    _inherit = "edi.backend"

    @property
    def output_template_model(self):
        return self.env["edi.exchange.template.output"]

    def _get_output_template(self, exchange_record):
        """Retrieve output template.

        :param exchange_record: record to generate.
        """
        tmpl = exchange_record.type_id.output_template_id
        if tmpl:
            return tmpl
        tmpl = self._get_output_template_fallback(exchange_record)
        return tmpl

    def _get_output_template_fallback(self, exchange_record):
        """Retrieve domains to lookup for templates by priority."""
        # Match by backend and allowed types
        base_domain = [
            ("backend_type_id", "=", self.backend_type_id.id),
            "|",
            ("allowed_type_ids", "=", exchange_record.type_id.id),
            ("allowed_type_ids", "=", False),
        ]
        candidates = self.output_template_model.search(base_domain)
        # Take the 1st one having allowed_type_ids set
        return fields.first(candidates.sorted(lambda x: 0 if x.allowed_type_ids else 1))
