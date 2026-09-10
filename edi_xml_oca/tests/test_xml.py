# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.exceptions import UserError
from odoo.tests.common import tagged

from odoo.addons.component.tests.common import TransactionComponentCase
from odoo.addons.edi_core_oca.tests.common import EDIBackendTestMixin

from .common import XMLTestCaseMixin

TEST_XML = """<?xml version="1.0" encoding="UTF-8"?>
<xs:element
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    name="shoesize"
    type="shoetype"
    />
"""


@tagged("-at_install", "post_install")
class XMLTestCase(TransactionComponentCase, EDIBackendTestMixin, XMLTestCaseMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # Demo data is not installed by default anymore: build our own backend.
        cls.backend = cls._get_backend()
        cls.handler = cls.backend._find_component(
            cls.backend._name,
            ["edi.xml"],
            work_ctx={"schema_path": "edi_xml_oca:tests/fixtures/Test.xsd"},
        )

    def test_xml_schema_fail(self):
        with self.assertRaises(ValueError):
            self.backend._find_component(
                self.backend._name, ["edi.xml"], work_ctx={"schema_path": "Nothing"}
            )
        with self.assertRaises(AttributeError):
            self.backend._find_component(
                self.backend._name, ["edi.xml"], work_ctx={"no_schema": "Nothing"}
            )

    def test_xml_schema_validation(self):
        with self.assertRaises(UserError):
            self.handler.validate(TEST_XML, raise_on_fail=True)

        self.handler = self.backend._find_component(
            self.backend._name,
            ["edi.xml"],
            work_ctx={"schema_path": "edi_xml_oca:tests/fixtures/simple_schema.xsd"},
        )

        SIMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
        <Person>
            <Name>Mitchell Admin</Name>
            <Age>30</Age>
            <Email>mitchell@test.com</Email>
        </Person>
        """
        # Valid XML raises no exception
        self.handler.validate(SIMPLE_XML, raise_on_fail=True)

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
