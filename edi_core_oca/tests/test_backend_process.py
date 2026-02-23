# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64

from freezegun import freeze_time
from psycopg2 import IntegrityError

from odoo import fields
from odoo.exceptions import UserError
from odoo.orm.model_classes import add_to_registry
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
        from .fake_models import EdiTestExecution

        add_to_registry(cls.registry, EdiTestExecution)
        cls.registry._setup_models__(cls.env.cr, ["edi.framework.test.execution"])
        cls.registry.init_models(
            cls.env.cr, ["edi.framework.test.execution"], {"models_to_check": True}
        )
        cls.addClassCleanup(cls.registry.__delitem__, "edi.framework.test.execution")
        cls.ExecutionAbstractModel = cls.env["edi.framework.test.execution"]
        cls.model = cls.env["ir.model"]._get("edi.framework.test.execution")
        cls.exchange_type_in.generate_model_id = cls.model
        cls.exchange_type_in.process_model_id = cls.model
        cls.exchange_type_in.input_validate_model_id = cls.model

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
        self.record._set_file_content(f"TEST {self.record.id}")
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
        record._set_file_content(f"TEST {record.id}")
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

    # TODO: test ack file are processed
