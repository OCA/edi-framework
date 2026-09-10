# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

from .common import XMLTestCaseMixin

TEST_XML = """<?xml version="1.0" encoding="UTF-8"?>
<xs:element
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    name="shoesize"
    type="shoetype"
    />
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
            self.handler.validate("Nothing", TEST_XML)

    def test_xml_schema_validation(self):
        with self.assertRaises(UserError):
            self.handler.validate(self.schema_path, TEST_XML, raise_on_fail=True)

        SIMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
        <Person>
            <Name>Mitchell Admin</Name>
            <Age>30</Age>
            <Email>mitchell@test.com</Email>
        </Person>
        """
        # Valid XML raises no exception
        self.handler.validate(
            "edi_xml_oca:tests/fixtures/simple_schema.xsd",
            SIMPLE_XML,
            raise_on_fail=True,
        )

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
