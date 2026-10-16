# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase
from odoo.tools import file_open

from odoo.addons.edi_core_oca.exceptions import EDIValidationError
from odoo.addons.edi_core_oca.tests.common import EDIBackendTestMixin

from .common import XMLTestCaseMixin

TEST_XML = """<?xml version="1.0" encoding="UTF-8"?>
<xs:element
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    name="shoesize"
    type="shoetype"
    />
"""

SIMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Person>
    <Name>Mitchell Admin</Name>
    <Age>30</Age>
    <Email>mitchell@test.com</Email>
</Person>
"""


class XMLTestCase(TransactionCase, XMLTestCaseMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.handler = cls.env["edi.xml"]
        cls.schema_path = "edi_xml_oca:tests/fixtures/Test.xsd"

    def test_xml_schema_fail(self):
        with self.assertRaises(ValueError):
            self.handler._validate_xml("Nothing", TEST_XML)

    def test_xml_schema_validation(self):
        with self.assertRaises(UserError):
            self.handler._validate_xml(self.schema_path, TEST_XML)
        # Valid XML raises no exception
        self.handler._validate_xml(
            "edi_xml_oca:tests/fixtures/simple_schema.xsd", SIMPLE_XML
        )

    def test_xml_schema_attachment(self):
        with self.assertRaises(FileNotFoundError):
            self.handler._validate_xml("simple_schema.xsd", SIMPLE_XML)
        with file_open("edi_xml_oca/tests/fixtures/simple_schema.xsd", "rb") as xsd:
            self.env["ir.attachment"].create(
                {"name": "simple_schema.xsd", "raw": xsd.read()}
            )
        self.handler._validate_xml("simple_schema.xsd", SIMPLE_XML)

    def test_listify(self):
        self.assertEqual(self.handler._listify(None), [])
        self.assertEqual(self.handler._listify([]), [])
        self.assertEqual(self.handler._listify({"a": "1"}), [{"a": "1"}])
        self.assertEqual(
            self.handler._listify([{"a": "1"}, {"a": "2"}]),
            [{"a": "1"}, {"a": "2"}],
        )

    def test_listify_parsed_xml(self):
        """A repeatable element has no stable shape: that's what _listify is for."""
        one = self.handler.parse_xml("<root><item>a</item></root>")
        several = self.handler.parse_xml("<root><item>a</item><item>b</item></root>")
        self.assertEqual(one["item"], "a")
        self.assertEqual(several["item"], ["a", "b"])
        self.assertEqual(self.handler._listify(one["item"]), ["a"])
        self.assertEqual(self.handler._listify(several["item"]), ["a", "b"])

    def test_xml(self):
        data = self.handler.parse_xml(TEST_XML)
        self.assertEqual(
            data,
            {
                "@xmlns:xs": "http://www.w3.org/2001/XMLSchema",
                "@name": "shoesize",
                "@type": "shoetype",
            },
        )


class XMLValidateHandlerTestCase(TransactionCase, EDIBackendTestMixin):
    @classmethod
    def _get_backend_type(cls):
        return cls.env["edi.backend.type"].create(
            {"name": "Test XML backend type", "code": "test_edi_xml"}
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.backend = cls._get_backend()
        xml_model = cls.env["ir.model"]._get("edi.xml")
        cls.exchange_type_in = cls._create_exchange_type(
            name="Test XML input",
            code="test_xml_input",
            direction="input",
            input_validate_model_id=xml_model.id,
            advanced_settings_edit="""
execution_model:
  input_validate:
    env_ctx:
      edi_xml_schema_path: edi_xml_oca:tests/fixtures/simple_schema.xsd
""",
        )
        cls.exchange_type_out = cls._create_exchange_type(
            name="Test XML output",
            code="test_xml_output",
            direction="output",
            output_validate_model_id=xml_model.id,
        )

    def _create_record(self, exchange_type, content=None):
        record = self.backend.create_record(exchange_type.code, {})
        if content:
            record._set_file_content(content)
        return record

    def test_is_validator(self):
        xml_model = self.env["ir.model"]._get("edi.xml")
        self.assertTrue(xml_model.is_edi_input_validator)
        self.assertTrue(xml_model.is_edi_output_validator)

    def test_input_validate(self):
        record = self._create_record(self.exchange_type_in, SIMPLE_XML)
        self.backend._validate_data(record)
        record = self._create_record(self.exchange_type_in, TEST_XML)
        with self.assertRaises(EDIValidationError):
            self.backend._validate_data(record)

    def test_output_validate_value(self):
        record = self._create_record(self.exchange_type_out)
        # No schema configured
        with self.assertRaises(EDIValidationError):
            self.backend._validate_data(record, value=SIMPLE_XML)
        self.exchange_type_out.advanced_settings_edit = """
execution_model:
  output_validate:
    env_ctx:
      edi_xml_schema_path: edi_xml_oca:tests/fixtures/simple_schema.xsd
"""
        self.backend._validate_data(record, value=SIMPLE_XML)
        with self.assertRaises(EDIValidationError):
            self.backend._validate_data(record, value=TEST_XML)
