# Copyright 2020 ACSONE
# Copyright 2021 Camptocamp
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from unittest import mock

from freezegun import freeze_time
from odoo_test_helper import FakeModelLoader

from odoo import fields, tools
from odoo.exceptions import UserError

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

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.ExecutionAbstractModel.reset_faked("generate")
        self.ExecutionAbstractModel.reset_faked("send")
        self.ExecutionAbstractModel.reset_faked("check")

    def test_generate_record_output(self):
        self.record.with_context(fake_output="yeah!").action_exchange_generate()
        self.assertEqual(self.record._get_file_content(), "yeah!")

    def test_generate_record_output_pdf(self):
        pdf_content = tools.file_open(
            "addons/edi_core_oca/tests/result.pdf", mode="rb"
        ).read()
        self.record.with_context(fake_output=pdf_content).action_exchange_generate()

    def test_send_record(self):
        self.record.write({"edi_exchange_state": "output_pending"})
        self.record._set_file_content("TEST %d" % self.record.id)
        self.assertFalse(self.record.exchanged_on)
        with freeze_time("2020-10-21 10:00:00"):
            self.record.action_exchange_send()
        self.assertTrue(
            self.ExecutionAbstractModel.check_called_for(self.record, "send")
        )
        self.assertRecordValues(self.record, [{"edi_exchange_state": "output_sent"}])
        self.assertEqual(
            fields.Datetime.to_string(self.record.exchanged_on), "2020-10-21 10:00:00"
        )

    def test_send_record_with_error(self):
        self.record.write({"edi_exchange_state": "output_pending"})
        self.record._set_file_content("TEST %d" % self.record.id)
        self.assertFalse(self.record.exchanged_on)
        self.record.with_context(
            test_break_send="OOPS! Something went wrong :("
        ).action_exchange_send()
        self.assertTrue(
            self.ExecutionAbstractModel.check_called_for(self.record, "send")
        )
        self.assertRecordValues(
            self.record,
            [
                {
                    "edi_exchange_state": "output_error_on_send",
                    "exchange_error": "OOPS! Something went wrong :(",
                }
            ],
        )
        self.assertIn(
            "OOPS! Something went wrong :(", self.record.exchange_error_traceback
        )

    def test_send_invalid_direction(self):
        vals = {
            "model": self.partner._name,
            "res_id": self.partner.id,
        }
        record = self.backend.create_record("test_csv_input", vals)
        with mock.patch.object(type(self.backend), "_exchange_send") as mocked:
            mocked.return_value = "AAA"
            with self.assertRaises(UserError) as err:
                record.action_exchange_send()
            self.assertEqual(
                err.exception.args[0],
                "Record ID=%d is not meant to be sent!" % record.id,
            )
            mocked.assert_not_called()

    def test_send_not_generated_record(self):
        vals = {
            "model": self.partner._name,
            "res_id": self.partner.id,
        }
        record = self.backend.create_record("test_csv_output", vals)
        with mock.patch.object(type(self.backend), "_exchange_send") as mocked:
            mocked.return_value = "AAA"
            with self.assertRaises(UserError) as err:
                record.action_exchange_send()
            self.assertEqual(
                err.exception.args[0], "Record ID=%d has no file to send!" % record.id
            )
            mocked.assert_not_called()
