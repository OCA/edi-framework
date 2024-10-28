# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simahaw@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = [
        "sale.order",
        "edi.exchange.consumer.mixin",
    ]
    edi_disable_auto = fields.Boolean()


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = [
        "sale.order.line",
        "edi.exchange.consumer.mixin",
        "edi.id.mixin",
    ]

    edi_disable_auto = fields.Boolean(related="order_id.edi_disable_auto")
