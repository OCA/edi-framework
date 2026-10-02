# Copyright 2022 Creu Blanca
# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

from odoo import models


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "edi.exchange.consumer.mixin"]

    # Override all methods to trigger EDI exchange after picking state changes.
    # ``stock.picking.state`` is computed so we cannot rely
    # on the write as done by the consumer mixin.`
    def action_confirm(self):
        with self._edi_exchange_event_trigger():
            result = super().action_confirm()
        return result

    def _action_done(self):
        with self._edi_exchange_event_trigger():
            result = super()._action_done()
        return result

    def action_cancel(self):
        with self._edi_exchange_event_trigger():
            result = super().action_cancel()
        return result

    @contextmanager
    def _edi_exchange_event_trigger(self):
        for picking in self:
            picking._event("on_edi_stock_picking_before_state_change").notify(
                picking, state=picking.state
            )
        yield
        for picking in self:
            picking._event("on_edi_stock_picking_state_change").notify(
                picking, state=picking.state
            )
