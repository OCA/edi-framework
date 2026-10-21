# Copyright 2025 Camptocamp
# Copyright 2025 Dixmit
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class EdiExchangeConsumerMixin(models.AbstractModel):
    _inherit = "edi.exchange.consumer.mixin"

    def _manual_notify_edi_generation(self, exchange_record):
        self._event("on_edi_generate_manual").notify(self, exchange_record)
        return super()._manual_notify_edi_generation(exchange_record)

    def write(self, vals):
        # Generic event to match a state change
        # TODO: this can be added to component_event for models having the state field
        state_change = "state" in vals and "state" in self._fields
        if state_change:
            for rec in self:
                rec._event(f"on_edi_{self._table}_before_state_change").notify(
                    rec, state=vals["state"]
                )
        res = super().write(vals)
        if state_change:
            for rec in self:
                rec._event(f"on_edi_{self._table}_state_change").notify(
                    rec, state=vals["state"]
                )
        return res
