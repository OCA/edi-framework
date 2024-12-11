# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import xmltodict
from lxml import etree

from odoo import modules
from odoo.exceptions import UserError
from odoo.tools.xml_utils import _check_with_xsd

from odoo.addons.component.core import Component


class XMLHandler(Component):
    """Validate and parse XML."""

    _name = "edi.xml.handler"
    _inherit = "edi.component.base.mixin"
    _usage = "edi.xml"

    _work_context_validate_attrs = ["schema_path"]

    def __init__(self, work_context):
        super().__init__(work_context)
        for key in self._work_context_validate_attrs:
            if not hasattr(work_context, key):
                raise AttributeError(f"`{key}` is required for this component!")

        self.schema_path, self.schema = self._get_xsd_schema()

    def _get_xsd_schema(self):
        """Lookup and parse the XSD schema."""
        try:
            mod_name, path = self.work.schema_path.split(":")
        except ValueError as exc:
            raise ValueError("Path must be in the form `module:path`") from exc

        schema_path = modules.get_resource_path(mod_name, path)
        if not schema_path:
            return UserError(f"XSD schema file not found: {self.work.schema_path}")

        with open(schema_path, "r") as schema_file:
            return schema_path, etree.XMLSchema(etree.parse(schema_file))

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

    def validate(self, xml_content, raise_on_fail=False):
        """Validate XML content against XSD schema.

        :param xml_content: str containing xml data to validate
        :param raise_on_fail: turn on/off validation error exception on fail

        :return:
            * None if validation is ok or skipped
            * error string if `raise_on_fail` is False and validation fails
        """

        xml_content = (
            xml_content.encode("utf-8") if isinstance(xml_content, str) else xml_content
        )
        try:
            with open(self.schema_path, "r") as xsd_stream:
                _check_with_xsd(xml_content, xsd_stream)
        except FileNotFoundError as exc:
            if raise_on_fail:
                raise exc
            return "XSD schema file not found: %s" % self.schema_path
        except Exception as exc:
            if raise_on_fail:
                raise exc
            return str(exc)
