# Copyright 2023 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class EDIStateConsumerFake(models.Model):
    _name = "edi.state.consumer.fake"
    _inherit = [
        "edi.exchange.consumer.mixin",
        "edi.state.consumer.mixin",
    ]
    _description = "Model used only for test"

    name = fields.Char()
