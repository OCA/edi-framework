# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import base64

import chardet

from odoo.orm.model_classes import add_to_registry

from .common import EDIBackendCommonTestCase


class EDIBackendTestOutputCase(EDIBackendCommonTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        vals = {
            "model": cls.partner._name,
            "res_id": cls.partner.id,
        }
        cls.record = cls.backend.create_record("test_csv_output", vals)

    @classmethod
    def _setup_records(cls):  # pylint:disable=missing-return
        super()._setup_records()
        # Load fake models ->/
        from .fake_models import EdiTestExecution

        add_to_registry(cls.registry, EdiTestExecution)
        cls.registry._setup_models__(cls.env.cr, ["edi.framework.test.execution"])
        cls.registry.init_models(
            cls.env.cr, ["edi.framework.test.execution"], {"models_to_check": True}
        )
        cls.addClassCleanup(cls.registry.__delitem__, "edi.framework.test.execution")
        cls.ExecutionAbstractModel = cls.env["edi.framework.test.execution"]
        cls.model = cls.env["ir.model"]._get("edi.framework.test.execution")
        cls.exchange_type_out.generate_model_id = cls.model
        cls.exchange_type_out.send_model_id = cls.model

    def setUp(self):
        super().setUp()
        self.ExecutionAbstractModel.reset_faked("generate")

    def test_encoding_default(self):
        """
        Test default output/input encoding (UTF-8). Use string with special
        character to test the encoding applied.
        """
        self.backend.with_context(fake_output="Palmotićeva").exchange_generate(
            self.record
        )
        # Test decoding is applied correctly
        self.assertEqual(self.record._get_file_content(), "Palmotićeva")
        # Test encoding used
        content = base64.b64decode(self.record.exchange_file)
        encoding = chardet.detect(content)["encoding"].lower()
        self.assertEqual(encoding, "utf-8")

    def test_encoding(self):
        """
        Test specific output/input encoding. Use string with special
        character to test the encoding applied.
        """
        self.exchange_type_out.write({"encoding": "UTF-16"})
        self.backend.with_context(fake_output="Palmotićeva").exchange_generate(
            self.record
        )
        # Test decoding is applied correctly
        self.assertEqual(self.record._get_file_content(), "Palmotićeva")
        # Test encoding used
        content = base64.b64decode(self.record.exchange_file)
        encoding = chardet.detect(content)["encoding"].lower()
        self.assertEqual(encoding, "utf-16")

    def test_encoding_error_handler(self):
        self.exchange_type_out.write({"encoding": "ascii"})
        # By default, error handling raises error
        with self.assertRaises(UnicodeEncodeError):
            self.backend.with_context(fake_output="Palmotićeva").exchange_generate(
                self.record
            )
        self.exchange_type_out.write({"encoding_out_error_handler": "ignore"})
        self.backend.with_context(fake_output="Palmotićeva").exchange_generate(
            self.record
        )
        self.assertEqual(self.record._get_file_content(), "Palmotieva")

    def test_decoding_error_handler(self):
        self.backend.with_context(fake_output="Palmotićeva").exchange_generate(
            self.record
        )
        # Change encoding to ascii to check the decoding
        self.exchange_type_out.write({"encoding": "ascii"})
        # By default, error handling raises error
        with self.assertRaises(UnicodeDecodeError):
            content = self.record._get_file_content()
        self.exchange_type_out.write({"encoding_in_error_handler": "ignore"})
        content = self.record._get_file_content()
        self.assertEqual(content, "Palmotieva")
