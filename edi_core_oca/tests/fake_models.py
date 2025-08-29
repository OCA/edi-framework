# Copyright 2020 Dixmit
# @author: Enric Tobella
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from collections import defaultdict

from odoo import fields, models


class EdiExchangeConsumerTest(models.Model):
    _name = "edi.exchange.consumer.test"
    _inherit = ["edi.exchange.consumer.mixin"]

    _description = "Model used only for test"

    name = fields.Char()
    edi_config_ids = fields.Many2many(
        string="EDI Test Config Ids",
        comodel_name="edi.configuration",
        relation="test_edi_configuration_rel",
        column1="record_id",
        column2="conf_id",
        domain="[('model_name', '=', 'edi.exchange.consumer.test')]",
    )

    def _edi_config_field_relation(self):
        return self.edi_config_ids

    def _get_edi_exchange_record_name(self, exchange_record):
        return self.id


class EdiTestExecution(models.AbstractModel):
    _name = "edi.framework.test.execution"
    _inherit = [
        "edi.oca.handler.process",
        "edi.oca.handler.check",
        "edi.oca.handler.send",
        "edi.oca.handler.receive",
        "edi.oca.handler.output.validate",
        "edi.oca.handler.input.validate",
    ]
    _description = "Fake EDI execution model for testing purposes"

    FAKED_COLLECTOR = defaultdict(list)

    def _fake_it(self, exchange_record, kind):
        self.FAKED_COLLECTOR[kind].append(self._call_key(exchange_record))
        if self.env.context.get("test_break_" + kind):
            exception = self.env.context.get("test_break_" + kind, "YOU BROKE IT!")
            if not isinstance(exception, Exception):
                exception = ValueError(exception)
            raise exception
        update_values = self.env.context.get("fake_update_values")
        if update_values:
            exchange_record.write(update_values)
        return self.env.context.get("fake_output", self._call_key(exchange_record))

    @classmethod
    def _call_key(cls, rec):
        return f"{cls._name}: {rec.id}"

    @classmethod
    def reset_faked(cls, kind):
        cls.FAKED_COLLECTOR[kind] = []

    @classmethod
    def check_called_for(cls, rec, kind):
        return cls._call_key(rec) in cls.FAKED_COLLECTOR[kind]

    @classmethod
    def check_not_called_for(cls, rec, kind):
        return cls._call_key(rec) not in cls.FAKED_COLLECTOR[kind]

    def send(self, exchange_record):
        return self._fake_it(exchange_record, "send")

    def generate(self, exchange_record):
        return self._fake_it(exchange_record, "generate")

    def output_validate(self, exchange_record, **kw):
        return self._fake_it(exchange_record, "output_validate")

    def input_validate(self, exchange_record, **kw):
        return self._fake_it(exchange_record, "input_validate")

    def receive(self, exchange_record):
        return self._fake_it(exchange_record, "receive")

    def process(self, exchange_record):
        return self._fake_it(exchange_record, "process")

    def check(self, exchange_record):
        return self._fake_it(exchange_record, "check")


class EdiTestExecutionExtra(models.AbstractModel):
    _name = "edi.framework.test.execution.extra"
    _inherit = "edi.framework.test.execution"
    _description = "Fake EDI execution model for testing purposes with extra methods"
