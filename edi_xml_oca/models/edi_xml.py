# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import xmltodict

from odoo import models
from odoo.tools import file_path
from odoo.tools.xml_utils import _check_with_xsd


class EdiXml(models.AbstractModel):
    """Validate and parse XML."""

    _name = "edi.xml"
    _description = "EDI XML helper"

    @staticmethod
    def _resolve_schema_path(schema_path):
        """Lookup the XSD schema.

        :param schema_path: schema path as ``module:path``
        """
        try:
            mod_name, path = schema_path.split(":")
        except ValueError as exc:
            raise ValueError("Path must be in the form `module:path`") from exc
        return file_path(f"{mod_name}/{path}")

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

    def validate(self, schema_path, xml_content, raise_on_fail=False):
        """Validate XML content against XSD schema.

        :param schema_path: schema path as ``module:path``
        :param xml_content: str containing xml data to validate
        :param raise_on_fail: turn on/off validation error exception on fail

        :return:
            * None if validation is ok or skipped
            * error string if `raise_on_fail` is False and validation fails
        """
        resolved_path = self._resolve_schema_path(schema_path)
        xml_content = (
            xml_content.encode("utf-8") if isinstance(xml_content, str) else xml_content
        )
        try:
            with open(resolved_path) as xsd_stream:
                _check_with_xsd(xml_content, xsd_stream)
        except FileNotFoundError as exc:
            if raise_on_fail:
                raise exc
            return f"XSD schema file not found: {schema_path}"
        except Exception as exc:
            if raise_on_fail:
                raise exc
            return str(exc)
