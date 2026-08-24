# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64

from freezegun import freeze_time
from odoo_test_helper import FakeModelLoader
from psycopg2 import IntegrityError

from odoo import fields
from odoo.exceptions import UserError
from odoo.tools import mute_logger

from .common import EDIBackendCommonTestCase


class EDIBackendTestProcessCase(EDIBackendCommonTestCase):
    def setUp(self):
        super().setUp()
        self.loader = FakeModelLoader(self.env, self.__module__)
        self.loader.backup_registry()
        from .fake_models import EdiTestExecution

        self.loader.update_registry((EdiTestExecution,))
        self.ExecutionAbstractModel = self.env["edi.framework.test.execution"]
        self.model = self.env["ir.model"].search(
            [("model", "=", "edi.framework.test.execution")]
        )
        self.exchange_type_in.generate_model_id = self.model
        self.exchange_type_in.process_model_id = self.model
        self.exchange_type_in.input_validate_model_id = self.model
        vals = {
            "model": self.partner._name,
            "res_id": self.partner.id,
            "exchange_file": base64.b64encode(b"1234"),
        }
        self.record = self.backend.create_record("test_csv_input", vals)
        self.ExecutionAbstractModel.reset_faked("process")

    def tearDown(self):
        self.loader.restore_registry()
        super().tearDown()

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

    def test_process_record_with_integrity_error(self):
        # IntegrityError is permanent (e.g. a DB unique constraint
        # violation): retrying the same data would fail again, so it must
        # be swallowed and move the record to an error state instead of
        # being re-raised and leaving it stuck in "input_received".
        self.record.write({"edi_exchange_state": "input_received"})
        with self.assertRaisesRegex(IntegrityError, "SQL error"):
            self.record.with_context(
                test_break_process=IntegrityError("SQL error"),
                _edi_process_break_on_error=True,
            ).action_exchange_process()

        self.record.with_context(
            test_break_process=IntegrityError("SQL error")
        ).action_exchange_process()
        self.assertRecordValues(
            self.record,
            [
                {
                    "edi_exchange_state": "input_processed_error",
                    "exchange_error": "SQL error",
                }
            ],
        )

    # TODO: test ack file are processed
