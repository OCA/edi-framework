# Copyright 2025 Dixmit
# @author Enric Tobella
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class EdiOcaHandlerGenerate(models.AbstractModel):
    _name = "edi.oca.handler.generate"
    _description = "EDI OCA Handler Generate"

    def generate(self, exchange_record):
        pass


class EdiOcaHandlerInputValidate(models.AbstractModel):
    _name = "edi.oca.handler.input.validate"
    _description = "EDI OCA Handler Input Validate"

    def input_validate(self, exchange_record, **kw):
        pass


class EdiOcaHandlerOutputValidate(models.AbstractModel):
    _name = "edi.oca.handler.output.validate"
    _description = "EDI OCA Handler Output Validate"

    def output_validate(self, exchange_record, **kw):
        pass


class EdiOcaHandlerSend(models.AbstractModel):
    _name = "edi.oca.handler.send"
    _description = "EDI OCA Handler Send"

    def send(self, exchange_record):
        pass


class EdiOcaHandlerReceive(models.AbstractModel):
    _name = "edi.oca.handler.receive"
    _description = "EDI OCA Handler Receive"

    def receive(self, exchange_record):
        pass


class EdiOcaHandlerProcess(models.AbstractModel):
    _name = "edi.oca.handler.process"
    _description = "EDI OCA Handler Process"

    def process(self, exchange_record):
        pass


class EdiOcaHandlerCheck(models.AbstractModel):
    _name = "edi.oca.handler.check"
    _description = "EDI OCA Handler Check"

    def check(self, exchange_record):
        pass
