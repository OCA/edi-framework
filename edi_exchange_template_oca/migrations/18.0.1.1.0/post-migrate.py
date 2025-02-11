# Copyright 2025 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})

    # Look for templates w/ a type set and set them as allowed on the type
    # plus link the type to the template
    templates = env["edi.exchange.template.output"].search([("type_id", "!=", False)])
    for tmpl in templates:
        allowed_type = tmpl.type_id
        tmpl.type_id.output_template_id = tmpl
        tmpl.allowed_type_ids += allowed_type
        tmpl.type_id = None
        _logger.info(
            "Set output template %s on exchange type %s",
            tmpl.name,
            allowed_type.name,
        )

    # Look for types w/o a template
    # and find the template by code to set as output template
    types = env["edi.exchange.type"].search([("output_template_id", "=", False)])
    for t in types:
        settings = t.get_settings()
        generate_usage = settings.get("components", {}).get("generate", {}).get("usage")
        if generate_usage:
            templates = env["edi.exchange.template.output"].search(
                [
                    ("code", "=", generate_usage),
                    ("backend_type_id", "=", t.backend_type_id.id),
                ]
            )
            if len(templates) == 1:
                tmpl = templates[0]
                tmpl.allowed_type_ids += t
                t.output_template_id = tmpl
                _logger.info(
                    "Set output template %s on exchange type %s",
                    t.output_template_id.name,
                    t.name,
                )
                continue

        _logger.warning(
            "Cannot set a template for exchange type %s. "
            "Either no template found or multiple found.",
            t.name,
        )
