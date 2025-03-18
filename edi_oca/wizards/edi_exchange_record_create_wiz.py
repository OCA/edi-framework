# Copyright 2020 Creu Blanca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class EdiExchangeRecordCreateWiz(models.TransientModel):
    _inherit = "edi.exchange.record.create.wiz"

    def create_edi(self):
        action = super().create_edi()
        if action and action.get("res_model") and action.get("res_id"):
            record = self.env[self.model].browse(self.res_id)
            exchange_record = self.env[action.get("res_model")].browse(
                action.get("res_id")
            )
            record._event("on_edi_generate_manual").notify(record, exchange_record)
        return action
