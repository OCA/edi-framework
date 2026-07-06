# Copyright 2024 Trobz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# from odoo.addons.component.core import Component
from odoo import models

from odoo.addons.edi_core_oca.exceptions import EDINotImplementedError


class EDIExchangeEDIFACTOutGenerate(models.AbstractModel):
    _name = "edi.output.edifact.out.generate"
    _inherit = [
        "edi.oca.handler.generate",
    ]
    _description = "Process Generate Output EDIFact"

    def generate(self, exchange_record):
        exchange_record = self.env["edi.exchange.record"].browse(exchange_record.id)
        tmpl = exchange_record.backend_id._get_output_template(exchange_record)
        if tmpl:
            exchange_record = exchange_record.with_context(
                edi_framework_action="generate"
            )
            tmpl = tmpl.with_context(edi_framework_action="generate")
        if exchange_record:
            if exchange_record.model == "purchase.order" and exchange_record.res_id:
                order = self.env["purchase.order"].browse(exchange_record.res_id)
                if order:
                    data = order.edifact_purchase_generate_data(exchange_record)
                    return data

        raise EDINotImplementedError(
            self.env._("EDIFact generation process is not implemented yet")
        )
