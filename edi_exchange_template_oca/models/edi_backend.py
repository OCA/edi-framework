# Copyright 2020 ACSONE SA
# Copyright 2025 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class EDIBackend(models.Model):
    _inherit = "edi.backend"

    def _exchange_generate(self, exchange_record, **kw):
        # Template take precedence over component lookup
        tmpl = self._get_output_template(exchange_record)
        if tmpl:
            # FIXME: env_ctx is not propagated here as we bypass components completely.
            # It would be better to move this machinery inside a `generate` component.
            exchange_record = exchange_record.with_context(
                edi_framework_action="generate"
            )
            tmpl = tmpl.with_context(edi_framework_action="generate")
            return tmpl.exchange_generate(exchange_record, **kw)
        return super()._exchange_generate(exchange_record, **kw)

    @property
    def output_template_model(self):
        return self.env["edi.exchange.template.output"]

    def _get_output_template(self, exchange_record, code=None):
        """Retrieve output template.

        :param exchange_record: record to generate.
        :param code: explicit template code to lookup.
        """
        search = self.output_template_model.search
        tmpl = None
        code = code or exchange_record.type_id.code
        if code:
            domain = [("code", "=", code)]
            tmpl = search(domain, limit=1)
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
