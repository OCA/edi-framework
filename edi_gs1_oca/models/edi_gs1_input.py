# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class EdiGs1InputMixin(models.AbstractModel):
    """Common GS1 input processing mixin.

    Replaces the old ``edi.gs1.input.mixin`` component. Concrete processors
    inherit this mixin together with ``edi.oca.handler.process``.
    """

    _name = "edi.gs1.input.mixin"
    _description = "GS1 EDI input mixin"

    def _get_schema_path(self, exchange_record):
        settings = exchange_record.type_id.get_settings() or {}
        return settings.get("gs1", {}).get("schema_path")

    def _parse(self, exchange_record):
        schema_path = self._get_schema_path(exchange_record)
        content = exchange_record._get_file_content()
        return self.env["edi.gs1.xml"].parse_xml(schema_path, content)

    def _process_data(self, data, exchange_record):
        raise NotImplementedError()
