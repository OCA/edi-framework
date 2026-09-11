# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions, models

from odoo.addons.edi_core_oca.exceptions import EDIValidationError


class EdiGs1HandlerValidate(models.AbstractModel):
    """Validate GS1 exchange files against their XSD schema.

    Wired on exchange types via ``input_validate_model_id`` /
    ``output_validate_model_id``. The schema is read from the exchange type
    advanced settings::

        gs1:
          schema_path: edi_gs1_oca:static/schemas/.../Foo.xsd
    """

    _name = "edi.gs1.handler.validate"
    _inherit = ["edi.oca.handler.input.validate", "edi.oca.handler.output.validate"]
    _description = "GS1 EDI XSD validation handler"

    def _gs1_validate(self, exchange_record, value=None):
        settings = exchange_record.type_id.get_settings() or {}
        schema_path = settings.get("gs1", {}).get("schema_path")
        if not schema_path:
            return None
        content = value
        if content is None:
            content = exchange_record._get_file_content()
        if isinstance(content, bytes):
            content = content.decode()
        error = self.env["edi.xml"].validate(schema_path, content)
        if error:
            raise EDIValidationError(error)
        return None

    def input_validate(self, exchange_record, value=None, **kw):
        return self._gs1_validate(exchange_record, value=value)

    def output_validate(self, exchange_record, value=None, **kw):
        return self._gs1_validate(exchange_record, value=value)


class EdiGs1HandlerApplicationReceiptAck(models.AbstractModel):
    """Process GS1 applicationReceiptAcknowledgement.

    Wired on the input ack exchange type via ``process_model_id``.
    """

    _name = "edi.gs1.handler.application.receipt.ack"
    _inherit = ["edi.oca.handler.process", "edi.gs1.input.mixin"]
    _description = "GS1 process applicationReceiptAcknowledgement"

    def process(self, exchange_record, **kw):
        data = self._parse(exchange_record)
        self._process_data(data, exchange_record)
        return self.env._("applicationReceiptAcknowledgement processed")

    def _process_data(self, data, exchange_record):
        if not self.is_ok(data):
            # TODO: give a proper message based on the real state
            # options: ERROR, RECEIVED, WARNING
            raise exceptions.ValidationError(self.env._("Exchange not received"))

    def is_ok(self, data):
        return self._get_status(data) == "RECEIVED"

    def _get_status(self, data):
        xml = self.env["edi.xml"]
        acks = xml._listify(data.get("applicationReceiptAcknowledgement"))
        if not acks:
            # Maybe raise an EDIValidationError?
            raise exceptions.ValidationError(
                self.env._("applicationReceiptAcknowledgement element not found!")
            )
        levels = xml._listify(acks[0].get("applicationResponseDocumentLevel"))
        # options: ERROR, RECEIVED, WARNING
        return levels[0]["applicationResponseStatusCode"]
