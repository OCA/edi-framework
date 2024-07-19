# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = [
        "sale.order",
        "edi.utm.consumer.mixin",
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._edi_update_source(vals)
        return super().create(vals_list)
