# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo_test_helper import FakeModelLoader

from .common import EDIBackendCommonTestCase


class EDIBackendTestInputCase(EDIBackendCommonTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        vals = {
            "model": cls.partner._name,
            "res_id": cls.partner.id,
        }
        cls.record = cls.backend.create_record("test_csv_input", vals)

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
        cls.exchange_type_in.receive_model_id = cls.model
        cls.exchange_type_in.process_model_id = cls.model
        cls.exchange_type_in.input_validate_model_id = cls.model

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    @classmethod
    def _setup_context(cls):
        return dict(
            super()._setup_context(),
            _edi_receive_break_on_error=True,
            _edi_process_break_on_error=True,
        )

    def setUp(self):
        super().setUp()
        self.ExecutionAbstractModel.reset_faked("receive")

    def test_receive_record_nothing_todo(self):
        self.backend.with_context(fake_output="yeah!").exchange_receive(self.record)
        self.assertEqual(self.record._get_file_content(), "")
        self.assertRecordValues(self.record, [{"edi_exchange_state": "new"}])

    def test_receive_record(self):
        self.record.edi_exchange_state = "input_pending"
        self.backend.with_context(fake_output="yeah!").exchange_receive(self.record)
        self.assertEqual(self.record._get_file_content(), "yeah!")
        self.assertRecordValues(self.record, [{"edi_exchange_state": "input_received"}])

    def test_receive_no_allow_empty_file_record(self):
        self.record.edi_exchange_state = "input_pending"
        self.backend.with_context(
            fake_output="", _edi_receive_break_on_error=False
        ).exchange_receive(self.record)
        # Check the record
        msg = (
            "Empty files are not allowed for exchange type "
            f"{self.exchange_type_in.name} ({self.exchange_type_in.code})"
        )
        self.assertEqual(msg, self.record.exchange_error)
        self.assertIn(msg, self.record.exchange_error_traceback)
        self.assertEqual(self.record._get_file_content(), "")
        self.assertRecordValues(
            self.record, [{"edi_exchange_state": "input_receive_error"}]
        )

    def test_receive_allow_empty_file_record(self):
        self.record.edi_exchange_state = "input_pending"
        self.record.type_id.allow_empty_files_on_receive = True
        self.backend.with_context(
            fake_output="", _edi_receive_break_on_error=False
        ).exchange_receive(self.record)
        # Check the record
        self.assertEqual(self.record._get_file_content(), "")
        self.assertRecordValues(self.record, [{"edi_exchange_state": "input_received"}])
