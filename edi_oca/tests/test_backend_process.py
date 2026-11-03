# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64
from unittest import mock

from freezegun import freeze_time
from psycopg2 import IntegrityError

from odoo import fields
from odoo.exceptions import UserError
from odoo.tools import mute_logger

from .common import EDIBackendCommonComponentRegistryTestCase
from .fake_components import FakeInputProcess


class EDIBackendTestProcessCase(EDIBackendCommonComponentRegistryTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._build_components(
            # TODO: test all components lookup
            cls,
            FakeInputProcess,
        )
        vals = {
            "model": cls.partner._name,
            "res_id": cls.partner.id,
            "exchange_file": base64.b64encode(b"1234"),
        }
        cls.record = cls.backend.create_record("test_csv_input", vals)

    def setUp(self):
        super().setUp()
        FakeInputProcess.reset_faked()

    def test_process_record(self):
        self.record.write({"edi_exchange_state": "input_received"})
        with freeze_time("2020-10-22 10:00:00"):
            self.record.action_exchange_process()
        self.assertTrue(FakeInputProcess.check_called_for(self.record))
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
        self.assertTrue(FakeInputProcess.check_called_for(self.record))
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
        self.record.write({"edi_exchange_state": "input_received"})
        with self.assertRaises(IntegrityError):
            self.backend.with_context(
                test_break_process=IntegrityError("SQL error")
            ).exchange_process(self.record)
        self.assertRecordValues(self.record, [{"edi_exchange_state": "input_received"}])
        self.assertFalse(self.record.exchange_error)

    def test_process_record_with_error_rollback(self):
        self.record.write({"edi_exchange_state": "input_received"})
        partner_name = self.partner.name

        def _exchange_process(exchange_record):
            self.partner.name = "Partially processed"
            self.partner.flush_recordset()
            raise ValueError("OOPS! Something went wrong :(")

        with mock.patch.object(
            type(self.backend), "_exchange_process", side_effect=_exchange_process
        ):
            self.backend.exchange_process(self.record)
        self.assertRecordValues(
            self.record, [{"edi_exchange_state": "input_processed_error"}]
        )
        # The changes made before the error are rolled back
        self.partner.invalidate_recordset()
        self.assertEqual(self.partner.name, partner_name)

    # TODO: test ack file are processed
