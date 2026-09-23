# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import xmltodict
from lxml import etree

from odoo import exceptions, models
from odoo.tools import file_open
from odoo.tools.xml_utils import _check_with_xsd

from odoo.addons.edi_core_oca.exceptions import EDIValidationError


class EdiXml(models.AbstractModel):
    """Validate and parse XML.

    Can be used as input/output validator on exchange types. The XSD schema
    is read from the ``edi_xml_schema_path`` context key, set through the
    exchange type advanced settings::

        execution_model:
          input_validate:
            env_ctx:
              edi_xml_schema_path: my_module:path/to/schema.xsd
    """

    _name = "edi.xml"
    _inherit = ["edi.oca.handler.input.validate", "edi.oca.handler.output.validate"]
    _description = "EDI XML helper"

    @staticmethod
    def _resolve_schema_path(schema_path):
        """Turn the XSD schema path into an addon relative path.

        :param schema_path: schema path as ``module:path``
        :return: path as ``module/path``, as expected by `file_open`
        """
        try:
            mod_name, path = schema_path.split(":")
        except ValueError as exc:
            raise ValueError("Path must be in the form `module:path`") from exc
        return f"{mod_name}/{path}"

    def _xml_string_to_dict(self, xml_string, **kw):
        """Read xml_content and return a data dict.

        :param xml_string: str of XML file
        """
        parsed_dict = xmltodict.parse(xml_string, **kw)
        root_node = next(iter(parsed_dict))
        return parsed_dict[root_node]

    def parse_xml(self, file_content, **kw):
        """Read XML content.
        :param file_content: str of XML file
        :return: dict with final data
        """
        return self._xml_string_to_dict(file_content, **kw)

    @staticmethod
    def _listify(value):
        """Normalize a parsed value into a list.

        A repeatable element is mapped to a dict when the document holds a
        single occurrence and to a list when it holds several. Callers
        iterating on such an element need a stable shape.

        :param value: value read from a parsed XML dict
        :return: list, empty when the element is missing
        """
        if value is None:
            return []
        return value if isinstance(value, list) else [value]

    def input_validate(self, exchange_record, value=None, **kw):
        return self._validate_exchange(exchange_record, value=value)

    def output_validate(self, exchange_record, value=None, **kw):
        return self._validate_exchange(exchange_record, value=value)

    def _validate_exchange(self, exchange_record, value=None):
        """Validate the exchange content against the XSD set in the context.

        :param exchange_record: edi.exchange.record
        :param value: content to validate, defaults to the record file
        :raise EDIValidationError: missing schema or invalid content
        """
        schema = self.env.context.get("edi_xml_schema_path")
        if not schema:
            raise EDIValidationError(
                self.env._(
                    "No XSD schema configured for exchange type %(code)s",
                    code=exchange_record.type_id.code,
                )
            )
        content = value if value is not None else exchange_record._get_file_content()
        try:
            self._validate_xml(schema, content)
        except (
            exceptions.UserError,
            FileNotFoundError,
            ValueError,
            etree.LxmlError,
        ) as exc:
            raise EDIValidationError(str(exc)) from exc

    def _validate_xml(self, schema, xml_content):
        """Validate XML content against an XSD schema.

        :param schema: addon file as ``module:path``,
            or name of an ``ir.attachment`` ending with ``.xsd``
        :param xml_content: str or bytes containing xml data to validate
        :raise UserError: the content does not match the schema
        :raise FileNotFoundError: the schema is not found
        """
        xml_content = (
            xml_content.encode("utf-8") if isinstance(xml_content, str) else xml_content
        )
        if ":" in schema:
            with file_open(self._resolve_schema_path(schema)) as xsd_stream:
                _check_with_xsd(xml_content, xsd_stream)
        elif schema.endswith(".xsd"):
            # Schema and its imports are looked up in ir.attachment
            _check_with_xsd(xml_content, schema, env=self.env)
        else:
            raise ValueError(
                "Schema must be in the form `module:path` or an XSD attachment name"
            )
