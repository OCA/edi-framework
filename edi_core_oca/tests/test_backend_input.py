# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from psycopg2 import OperationalError

from odoo.orm.model_classes import add_to_registry

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
        from .fake_models import EdiTestExecution

        add_to_registry(cls.registry, EdiTestExecution)
        cls.registry._setup_models__(cls.env.cr, ["edi.framework.test.execution"])
        cls.registry.init_models(
            cls.env.cr, ["edi.framework.test.execution"], {"models_to_check": True}
        )
        cls.addClassCleanup(cls.registry.__delitem__, "edi.framework.test.execution")
        cls.ExecutionAbstractModel = cls.env["edi.framework.test.execution"]
        cls.model = cls.env["ir.model"]._get("edi.framework.test.execution")
        cls.exchange_type_in.receive_model_id = cls.model
        cls.exchange_type_in.process_model_id = cls.model
        cls.exchange_type_in.input_validate_model_id = cls.model

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

    def test_receive_record_with_operational_error(self):
        self.record.edi_exchange_state = "input_pending"
        with self.assertRaises(OperationalError):
            self.backend.with_context(
                test_break_receive=OperationalError("SQL error")
            ).exchange_receive(self.record)
        self.assertRecordValues(self.record, [{"edi_exchange_state": "input_pending"}])
        self.assertFalse(self.record.exchange_error)
