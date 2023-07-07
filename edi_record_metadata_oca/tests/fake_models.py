# Copyright 2023 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class EDIMetadataConsumerFake(models.Model):
    _name = "edi.metadata.consumer.fake"
    _inherit = [
        "edi.exchange.consumer.mixin",
    ]
    _description = "Model used only for test"

    name = fields.Char()
    number = fields.Float()
    a_date = fields.Date()
    a_datetime = fields.Datetime()

    def _edi_get_metadata_to_store(self, orig_vals):
        data = super()._edi_get_metadata_to_store(orig_vals)
        data.update(orig_vals)
        data["additional"] = True
        return data
