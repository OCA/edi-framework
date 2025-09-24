# Copyright 2025 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestExchangeType(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend_type = cls.env.ref("edi_core_oca.demo_edi_backend_type")
        cls.backend = cls.env.ref("edi_core_oca.demo_edi_backend")
        cls.type_out1 = cls.env["edi.exchange.type"].create(
            {
                "name": "Type output 1",
                "direction": "output",
                "code": "test_type_out1",
                "exchange_file_ext": "txt",
                "generate_model_id": cls.env.ref(
                    "edi_exchange_template_oca.model_edi_oca_template_handler"
                ).id,
                "backend_type_id": cls.backend_type.id,
            }
        )
        cls.type_out2 = cls.env["edi.exchange.type"].create(
            {
                "name": "Type output 2",
                "direction": "output",
                "code": "test_type_out2",
                "exchange_file_ext": "txt",
                "generate_model_id": cls.env.ref(
                    "edi_exchange_template_oca.model_edi_oca_template_handler"
                ).id,
                "backend_type_id": cls.backend_type.id,
            }
        )
        model = cls.env["edi.exchange.template.output"]
        qweb_tmpl = cls.env["ir.ui.view"].create(
            {
                "type": "qweb",
                "key": "edi_exchange.test_output1",
                "arch": """
            <t t-name="edi_exchange.test_output1">
                TEST
            </t>
            """,
            }
        )
        cls.tmpl_out1 = model.create(
            {
                "code": "tmpl_test_type_out1",
                "name": "Out 1",
                "backend_type_id": cls.backend_type.id,
                "template_id": qweb_tmpl.id,
                "output_type": "txt",
            }
        )
        cls.tmpl_out2 = model.create(
            {
                "code": "tmpl_test_type_out2",
                "name": "Out 2",
                "backend_type_id": cls.env.ref("edi_core_oca.demo_edi_backend_type").id,
                "template_id": qweb_tmpl.id,
                "output_type": "txt",
            }
        )
        vals = {
            # doesn't matter what model we use
            "model": cls.env.user._name,
            "res_id": cls.env.user.id,
            "type_id": cls.type_out2.id,
        }
        cls.record1 = cls.backend.create_record("test_type_out1", vals)
        vals = {
            # doesn't matter what model we use
            "model": cls.env.user._name,
            "res_id": cls.env.user.id,
            "type_id": cls.type_out2.id,
        }
        cls.record2 = cls.backend.create_record("test_type_out2", vals)

    def test_get_template_by_fallback(self):
        self.assertEqual(
            self.backend._get_output_template(self.record1), self.tmpl_out1
        )
        # Here's is shown the limitation of the fallback lookup by backend type:
        # if you have more than one template allowed for the same type,
        # the first one is returned.
        self.assertEqual(
            self.backend._get_output_template(self.record2), self.tmpl_out1
        )

    def test_get_template_allowed(self):
        # No match by code on both templates
        self.assertNotEqual(self.type_out1.code, self.tmpl_out1.code)
        self.assertNotEqual(self.type_out1.code, self.tmpl_out2.code)
        # Tmpl 2 is available for all types
        self.assertFalse(self.tmpl_out2.allowed_type_ids)
        # Tmpl 1 is explicitly set as allowed for type 1 -> we should get it 1st
        self.tmpl_out1.allowed_type_ids = self.type_out1
        self.assertEqual(
            self.backend._get_output_template(self.record1),
            self.tmpl_out1,
        )
        # Add a template, but still the 1st one is returned
        self.tmpl_out1.allowed_type_ids += self.type_out2
        self.assertEqual(
            self.backend._get_output_template(self.record1), self.tmpl_out1
        )

    def test_get_template_selected(self):
        self.type_out1.output_template_id = self.tmpl_out1
        self.type_out2.output_template_id = self.tmpl_out2
        self.tmpl_out1.allowed_type_ids = self.type_out1
        self.tmpl_out2.allowed_type_ids = self.type_out2
        self.assertEqual(
            self.backend._get_output_template(self.record1), self.tmpl_out1
        )
        self.assertEqual(
            self.backend._get_output_template(self.record2), self.tmpl_out2
        )
        # inverse
        with self.assertRaisesRegex(
            ValidationError, "Template not allowed for this type."
        ):
            self.type_out1.output_template_id = self.tmpl_out2
        with self.assertRaisesRegex(
            ValidationError, "Template not allowed for this type."
        ):
            self.type_out2.output_template_id = self.tmpl_out1
        self.tmpl_out1.allowed_type_ids = self.type_out2
        self.tmpl_out2.allowed_type_ids = self.type_out1
        self.type_out1.output_template_id = self.tmpl_out2
        self.type_out2.output_template_id = self.tmpl_out1
        self.assertEqual(
            self.backend._get_output_template(self.record1), self.tmpl_out2
        )
        self.assertEqual(
            self.backend._get_output_template(self.record2), self.tmpl_out1
        )
