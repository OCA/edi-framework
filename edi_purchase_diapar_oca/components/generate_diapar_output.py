from odoo import models

from odoo.addons.edi_core_oca.exceptions import EDINotImplementedError


class EdiOcaHandlerGenerate(models.AbstractModel):
    _name = "edi.output.diapar.handler"
    _inherit = [
        "edi.oca.handler.generate",
    ]
    _description = "EDI Handler Generate Output For Diapar"

    def generate(self, exchange_record):
        exchange_record = self.env["edi.exchange.record"].browse(exchange_record.id)
        tmpl = exchange_record.backend_id._get_output_template(exchange_record)
        if tmpl:
            exchange_record = exchange_record.with_context(
                edi_framework_action="generate"
            )
            tmpl = tmpl.with_context(edi_framework_action="generate")
            if exchange_record.model == "purchase.order" and exchange_record.res_id:
                order = self.env["purchase.order"].browse(exchange_record.res_id)
                if order:
                    return order.generate_template_output_diapar(
                        tmpl,
                        exchange_record,
                    )
        raise EDINotImplementedError(
            self.env._("Only purchase order with Diapar output template are supported.")
        )
