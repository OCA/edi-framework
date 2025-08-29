# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64

from freezegun import freeze_time
from odoo_test_helper import FakeModelLoader

from odoo import fields
from odoo.exceptions import UserError
from odoo.tools import mute_logger

from .common import EDIBackendCommonTestCase


class EDIBackendTestProcessCase(EDIBackendCommonTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        vals = {
            "model": cls.partner._name,
            "res_id": cls.partner.id,
            "exchange_file": base64.b64encode(b"1234"),
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
        cls.exchange_type_in.generate_model_id = cls.model
        cls.exchange_type_in.process_model_id = cls.model
        cls.exchange_type_in.input_validate_model_id = cls.model

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.ExecutionAbstractModel.reset_faked("process")

    def test_process_record(self):
        self.record.write({"edi_exchange_state": "input_received"})
        with freeze_time("2020-10-22 10:00:00"):
            self.record.action_exchange_process()
        self.assertTrue(
            self.ExecutionAbstractModel.check_called_for(self.record, "process")
        )
        self.assertRecordValues(
            self.record, [{"edi_exchange_state": "input_processed"}]
        )
        self.assertEqual(
            fields.Datetime.to_string(self.record.exchanged_on), "2020-10-22 10:00:00"
        )

    def test_process_record_with_error(self):
        self.record.write({"edi_exchange_state": "input_received"})
        self.record._set_file_content("TEST %d" % self.record.id)
        self.record.with_context(
            test_break_process="OOPS! Something went wrong :("
        ).action_exchange_process()
        self.assertTrue(
            self.ExecutionAbstractModel.check_called_for(self.record, "process")
        )
        self.assertRecordValues(
            self.record,
            [
                {
                    "edi_exchange_state": "input_processed_error",
                    "exchange_error": "OOPS! Something went wrong :(",
                }
            ],
        )
        self.assertIn(
            "OOPS! Something went wrong :(", self.record.exchange_error_traceback
        )

    @mute_logger("odoo.models.unlink")
    def test_process_no_file_record(self):
        self.record.write({"edi_exchange_state": "input_received"})
        self.record.exchange_file = False
        self.exchange_type_in.allow_empty_files_on_receive = False
        with self.assertRaises(UserError):
            self.record.action_exchange_process()

    @mute_logger("odoo.models.unlink")
    def test_process_allow_no_file_record(self):
        self.record.write({"edi_exchange_state": "input_received"})
        self.record.exchange_file = False
        self.exchange_type_in.allow_empty_files_on_receive = True
        self.record.action_exchange_process()
        self.assertEqual(self.record.edi_exchange_state, "input_processed")

    def test_process_outbound_record(self):
        vals = {
            "model": self.partner._name,
            "res_id": self.partner.id,
        }
        record = self.backend.create_record("test_csv_output", vals)
        record._set_file_content("TEST %d" % record.id)
        with self.assertRaises(UserError):
            record.action_exchange_process()

    # TODO: test ack file are processed
