# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import io
from contextlib import closing

import xmlschema

from odoo import models, tools
from odoo.tools import DotDict


class EdiGs1Xml(models.AbstractModel):
    """Validate and parse XML against a bundled XSD schema.

    Replaces the ``edi.xml`` component from the old ``edi_xml`` module
    (dropped in the new EDI OCA architecture). Schema paths use the
    ``module:relative/path.xsd`` notation.
    """

    _name = "edi.gs1.xml"
    _description = "GS1 EDI XML helper"

    @staticmethod
    def _resolve_schema_path(schema_path):
        try:
            mod_name, path = schema_path.split(":")
        except ValueError as exc:
            raise ValueError("Path must be in the form `module:path`") from exc
        return tools.file_path(f"{mod_name}/{path}")

    def _get_schema(self, schema_path):
        return xmlschema.XMLSchema(self._resolve_schema_path(schema_path))

    def parse_xml(self, schema_path, file_content, **kw):
        """Read XML content and return a data dict.

        :param schema_path: schema path as ``module:path``
        :param file_content: str of XML file
        :return: odoo.tools.DotDict with final data
        """
        schema = self._get_schema(schema_path)
        with closing(io.StringIO(file_content)) as fd:
            return DotDict(schema.to_dict(fd, **kw))

    def validate(self, schema_path, xml_content, raise_on_fail=False):
        """Validate XML content against the XSD schema.

        :param schema_path: schema path as ``module:path``
        :param xml_content: str containing xml data to validate
        :param raise_on_fail: turn on/off validation error exception on fail
        :return:
            * None if validation is ok
            * error string if `raise_on_fail` is False
        """
        schema = self._get_schema(schema_path)
        try:
            return schema.validate(xml_content)
        except xmlschema.validators.exceptions.XMLSchemaValidationError as err:
            if raise_on_fail:
                raise
            return str(err)
