# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from contextlib import contextmanager

from odoo import models


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = [
        "purchase.order",
        "edi.exchange.consumer.mixin",
    ]

    def button_confirm(self):
        with self._edi_purchase_order_state_change_trigger():
            result = super().button_confirm()
        return result

    def button_cancel(self):
        with self._edi_purchase_order_state_change_trigger():
            result = super().button_cancel()
        return result

    @contextmanager
    def _edi_purchase_order_state_change_trigger(self):
        for order in self:
            order._event("on_edi_purchase_order_state_change").notify(
                order, state=order.state
            )
        yield
