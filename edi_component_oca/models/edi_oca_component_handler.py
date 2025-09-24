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
    _name = "edi.oca.component.handler"
    _inherit = [
        "edi.oca.handler.generate",
        "edi.oca.handler.input.validate",
        "edi.oca.handler.output.validate",
        "edi.oca.handler.send",
        "edi.oca.handler.receive",
        "edi.oca.handler.process",
        "edi.oca.handler.check",
    ]
    _description = "Component Handler for EDI"

    def generate(self, exchange_record):
        component = exchange_record.backend_id._get_component(
            exchange_record, "generate"
        )
        if component:
            return component.generate()
        raise EDINotImplementedError("No component found to generate EDI document.")

    def input_validate(self, exchange_record, value=None, **kw):
        component = exchange_record.backend_id._get_component(
            exchange_record, "validate"
        )
        if component:
            return component.validate(value)
        raise EDINotImplementedError(
            "No component found to validate EDI document input."
        )

    def output_validate(self, exchange_record, value=None, **kw):
        component = exchange_record.backend_id._get_component(
            exchange_record, "validate"
        )
        if component:
            return component.validate(value)
        raise EDINotImplementedError(
            "No component found to validate EDI document output."
        )

    def send(self, exchange_record):
        component = exchange_record.backend_id._get_component(exchange_record, "send")
        if component:
            return component.send()
        raise EDINotImplementedError("No component found to send EDI document.")

    def receive(self, exchange_record):
        component = exchange_record.backend_id._get_component(
            exchange_record, "receive"
        )
        if component:
            return component.receive()
        raise EDINotImplementedError("No component found to receive EDI document.")

    def process(self, exchange_record):
        component = exchange_record.backend_id._get_component(
            exchange_record, "process"
        )
        if component:
            return component.process()
        raise EDINotImplementedError("No component found to process EDI document.")

    def check(self, exchange_record):
        component = exchange_record.backend_id._get_component(exchange_record, "check")
        if component:
            return component.check()
        raise EDINotImplementedError("No component found to check EDI document.")
