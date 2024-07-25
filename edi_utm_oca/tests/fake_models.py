# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class EDIUtmConsumerFake(models.Model):
    _name = "edi.utm.consumer.fake"
    _inherit = ["edi.exchange.consumer.mixin", "edi.utm.consumer.mixin"]
    _description = "Model used only for test"

    name = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._edi_update_source(vals)
        return super().create(vals_list)
