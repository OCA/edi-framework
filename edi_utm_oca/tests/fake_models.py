# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EDIUtmConsumerFake(models.Model):
    _name = "edi.utm.consumer.fake"
    _description = "Model used only for test"
    _inherit = "edi.exchange.consumer.mixin"

    name = fields.Char()
    source_id = fields.Many2one("utm.source", "Source", readonly=True)
