# Copyright 2025 Dixmit
# @author Enric Tobella
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# Copyright 2025 Dixmit
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging

from odoo import models

from odoo.addons.edi_core_oca.exceptions import EDINotImplementedError

_logger = logging.getLogger(__name__)


class EdiOcaHandlerGenerate(models.AbstractModel):
    _name = "edi.oca.template.handler"
    _inherit = [
        "edi.oca.handler.generate",
    ]
    _description = "Exchange Template Handler for EDI"

    def generate(self, exchange_record):
        tmpl = exchange_record.backend_id._get_output_template(exchange_record)
        if tmpl:
            exchange_record = exchange_record.with_context(
                edi_framework_action="generate"
            )
            tmpl = tmpl.with_context(edi_framework_action="generate")
            return tmpl.exchange_generate(exchange_record)
        raise EDINotImplementedError("No EDI template found.")
