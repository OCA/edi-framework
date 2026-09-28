# Copyright 2024 Trobz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo import models


class EDIExchangeEDIFACTInput(models.Model):
    _name = "edi.input.process.edifact.input"
    _inherit = ["edi.oca.handler.process"]
    _description = "Input process despatch advice from EDIFact"

    def process(self, exchange_record):
        """Process incoming EDIFACT record and confirm record."""
        file_content = exchange_record._get_file_content()
        wizard = self.env["purchase.order.import"].create(
            {
                "import_type": "edifact",
                "order_file": base64.b64encode(file_content.encode()),
                "order_filename": exchange_record.exchange_filename,
            }
        )
        file_name = exchange_record.exchange_filename
        action = wizard.import_order_button()
        if action and action.get("res_model", False):
            exchange_record.update(
                {
                    "model": action["res_model"],
                    "res_id": action["res_id"],
                }
            )
            exchange_record.exchange_filename = file_name

        return self.env._("Process incoming EDIFACT completed!")
