# Copyright 2023
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.component.core import Component


class EDIExchangeAccountMoveGenerate(Component):
    _name = "edi.output.edifact.account.move.generate"
    _inherit = "edi.component.output.mixin"
    _usage = "output.generate.account.move"
    _apply_on = ["account.move"]

    def generate(self):
        data = False
        exchange_record = self.exchange_record
        if exchange_record.res_id:
            move = self.record
            data = move.edifact_invoice_generate_data()
        return data
