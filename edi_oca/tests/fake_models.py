# Copyright 2020 Creu Blanca
# @author: Enric Tobella
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class EdiExchangeConsumerTest(models.Model):
    _name = "edi.exchange.consumer.test"
    _inherit = ["edi.exchange.consumer.mixin"]
    _description = "Model used only for test"

    name = fields.Char()
    edi_config_ids = fields.Many2many(
        string="EDI Purchase Config Ids",
        comodel_name="edi.configuration",
        relation="test_edi_configuration_rel",
        column1="record_id",
        column2="conf_id",
        domain="[('model_name', '=', 'edi.exchange.consumer.test')]",
    )

    def _get_edi_exchange_record_name(self, exchange_record):
        return self.id
