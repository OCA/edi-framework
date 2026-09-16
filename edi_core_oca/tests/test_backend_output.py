# Copyright 2020 ACSONE
# Copyright 2021 Camptocamp
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from unittest import mock

from freezegun import freeze_time
from odoo_test_helper import FakeModelLoader
from psycopg2 import OperationalError

from odoo import fields, tools
from odoo.exceptions import UserError

from ..utils import EDIExchangeActionResult
from .common import EDIBackendCommonTestCase


class EDIBackendTestOutputCase(EDIBackendCommonTestCase):
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
        self.exchange_type_out.generate_model_id = self.model
        self.exchange_type_out.send_model_id = self.model
        self.exchange_type_out.output_validate_model_id = self.model
        vals = {
            "model": self.partner._name,
            "res_id": self.partner.id,
        }
        self.record = self.backend.create_record("test_csv_output", vals)
        self.ExecutionAbstractModel.reset_faked("generate")
        self.ExecutionAbstractModel.reset_faked("send")
        self.ExecutionAbstractModel.reset_faked("check")

    def tearDown(self):
        self.loader.restore_registry()
        super().tearDown()

    def test_generate_record_output(self):
        self.record.with_context(fake_output="yeah!").action_exchange_generate()
        self.assertEqual(self.record._get_file_content(), "yeah!")

    def test_generate_record_output_with_custom_action_result_message(self):
        with mock.patch(
            "odoo.addons.edi_core_oca.models.edi_backend.EDIBackend._exchange_generate",
            return_value=EDIExchangeActionResult(
                output="yeah!", message="Generated with custom message"
            ),
        ):
            message = self.record.action_exchange_generate()
        self.assertEqual(message, "Generated with custom message")
        self.assertEqual(self.record._get_file_content(), "yeah!")

    def test_generate_record_output_with_legacy_override_string(self):
        with mock.patch(
            "odoo.addons.edi_core_oca.models.edi_backend.EDIBackend._exchange_generate",
            return_value=EDIExchangeActionResult.from_result("yeah!"),
        ):
            message = self.record.action_exchange_generate()
        self.assertEqual(message, self.record._exchange_status_message("generate_ok"))
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
            self.assertRecordValues(
                self.record, [{"edi_exchange_state": "output_sent"}]
            )
            self.assertEqual(
                fields.Datetime.to_string(self.record.exchanged_on),
                "2020-10-21 10:00:00",
            )

    def test_send_record_with_custom_action_result(self):
        self.record.write({"edi_exchange_state": "output_pending"})
        self.record._set_file_content(f"TEST {self.record.id}")
        with mock.patch(
            "odoo.addons.edi_core_oca.models.edi_backend.EDIBackend._exchange_send",
            return_value=EDIExchangeActionResult(
                output="send-payload", message="Sent with custom message"
            ),
        ):
            res = self.record.action_exchange_send()
        self.assertEqual(res, "Sent with custom message")
        self.assertRecordValues(self.record, [{"edi_exchange_state": "output_sent"}])

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

    def test_send_record_with_error_triggers_notify_error(self):
        self.record.write({"edi_exchange_state": "output_pending"})
        self.record._set_file_content(f"TEST {self.record.id}")
        conf = self._make_global_error_conf(self.record.type_id)
        self.record.with_context(
            test_break_send="OOPS! Something went wrong :("
        ).action_exchange_send()
        # The error event must fire so downstream notifications (e.g.
        # edi_notification_oca activities) are triggered.
        self.assertEqual(conf.description, "error-event-fired")

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

    def test_send_record_with_operational_error(self):
        self.record.write({"edi_exchange_state": "output_pending"})
        self.record._set_file_content("TEST %d" % self.record.id)
        with self.assertRaises(OperationalError):
            self.backend.with_context(
                test_break_send=OperationalError("SQL error")
            ).exchange_send(self.record)
        self.assertRecordValues(self.record, [{"edi_exchange_state": "output_pending"}])
        self.assertFalse(self.record.exchange_error)
