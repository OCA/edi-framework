# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64

from odoo_test_helper import FakeModelLoader

from ..exceptions import EDIValidationError
from .common import EDIBackendCommonTestCase


class EDIBackendTestValidateCase(EDIBackendCommonTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        vals = {
            "model": cls.partner._name,
            "res_id": cls.partner.id,
            "exchange_file": base64.b64encode(b"1234"),
        }
        cls.record_in = cls.backend.create_record("test_csv_input", vals)
        vals.pop("exchange_file")
        cls.record_out = cls.backend.create_record("test_csv_output", vals)

    @classmethod
    def _setup_records(cls):  # pylint:disable=missing-return
        super()._setup_records()
        # Load fake models ->/
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .fake_models import EdiTestExecution

        cls.loader.update_registry((EdiTestExecution,))
        cls.ExecutionAbstractModel = cls.env["edi.framework.test.execution"]
        cls.model = cls.env["ir.model"].search(
            [("model", "=", "edi.framework.test.execution")]
        )
        cls.exchange_type_out.generate_model_id = cls.model
        cls.exchange_type_out.send_model_id = cls.model
        cls.exchange_type_out.output_validate_model_id = cls.model
        cls.exchange_type_in.receive_model_id = cls.model
        cls.exchange_type_in.process_model_id = cls.model
        cls.exchange_type_in.input_validate_model_id = cls.model

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.ExecutionAbstractModel.reset_faked("input_validate")
        self.ExecutionAbstractModel.reset_faked("receive")
        self.ExecutionAbstractModel.reset_faked("generate")
        self.ExecutionAbstractModel.reset_faked("output_validate")

    def test_receive_validate_record(self):
        self.record_in.write({"edi_exchange_state": "input_pending"})
        self.backend.exchange_receive(self.record_in)
        self.assertTrue(
            self.ExecutionAbstractModel.check_called_for(
                self.record_in, "input_validate"
            )
        )
        self.assertRecordValues(
            self.record_in, [{"edi_exchange_state": "input_received"}]
        )

    def test_receive_validate_record_error(self):
        self.record_in.write({"edi_exchange_state": "input_pending"})
        exc = EDIValidationError("Data seems wrong!")
        self.backend.with_context(test_break_input_validate=exc).exchange_receive(
            self.record_in
        )
        self.assertTrue(
            self.ExecutionAbstractModel.check_called_for(
                self.record_in, "input_validate"
            )
        )
        self.assertRecordValues(
            self.record_in,
            [
                {
                    "edi_exchange_state": "validate_error",
                    "exchange_error": "Data seems wrong!",
                }
            ],
        )
        self.assertIn("Data seems wrong!", self.record_in.exchange_error_traceback)

    def test_generate_validate_record(self):
        self.record_out.write({"edi_exchange_state": "new"})
        self.backend.exchange_generate(self.record_out)
        self.assertTrue(
            self.ExecutionAbstractModel.check_called_for(
                self.record_out, "output_validate"
            )
        )
        self.assertRecordValues(
            self.record_out, [{"edi_exchange_state": "output_pending"}]
        )

    def test_generate_validate_record_error(self):
        self.record_out.write({"edi_exchange_state": "new"})
        exc = EDIValidationError("Data seems wrong!")
        self.backend.with_context(test_break_output_validate=exc).exchange_generate(
            self.record_out
        )
        self.assertTrue(
            self.ExecutionAbstractModel.check_called_for(
                self.record_out, "output_validate"
            )
        )
        self.assertRecordValues(
            self.record_out,
            [
                {
                    "edi_exchange_state": "validate_error",
                    "exchange_error": "Data seems wrong!",
                }
            ],
        )
        self.assertIn("Data seems wrong!", self.record_out.exchange_error_traceback)

    def test_validate_record_error_regenerate(self):
        self.record_out.write({"edi_exchange_state": "new"})
        exc = EDIValidationError("Data seems wrong!")
        self.backend.with_context(test_break_output_validate=exc).exchange_generate(
            self.record_out
        )
        self.assertRecordValues(
            self.record_out,
            [
                {
                    "edi_exchange_state": "validate_error",
                }
            ],
        )
        self.record_out.with_context(fake_output="yeah!").action_regenerate()
        self.assertEqual(self.record_out._get_file_content(), "yeah!")
        self.assertRecordValues(
            self.record_out,
            [
                {
                    "edi_exchange_state": "output_pending",
                }
            ],
        )
