# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo_test_helper import FakeModelLoader

from odoo.tools import mute_logger

from .common import EDIBackendCommonTestCase

LOGGERS = (
    "odoo.addons.edi_core_oca.models.edi_backend",
    "odoo.addons.queue_job.delay",
    "odoo.addons.edi_exchange_template_oca.models.edi_backend",
)


class EDIBackendTestCronCase(EDIBackendCommonTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner2 = cls.env.ref("base.res_partner_10")
        cls.partner3 = cls.env.ref("base.res_partner_12")
        cls.record1 = cls.backend.create_record(
            "test_csv_output", {"model": cls.partner._name, "res_id": cls.partner.id}
        )
        cls.record2 = cls.backend.create_record(
            "test_csv_output", {"model": cls.partner._name, "res_id": cls.partner2.id}
        )
        cls.record3 = cls.backend.create_record(
            "test_csv_output", {"model": cls.partner._name, "res_id": cls.partner3.id}
        )
        cls.records = cls.record1 + cls.record1 + cls.record3

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

    @mute_logger(*LOGGERS)
    def test_exchange_generate_new_no_auto(self):
        # No content ready to be sent, no auto-generate, nothing happens
        for rec in self.records:
            self.assertEqual(rec.edi_exchange_state, "new")
        self.backend._cron_check_output_exchange_sync()
        for rec in self.records:
            self.assertEqual(rec.edi_exchange_state, "new")

    @mute_logger(*LOGGERS)
    def test_exchange_generate_new_auto_skip_send(self):
        self.exchange_type_out.exchange_file_auto_generate = True
        # No content ready to be sent, will get the content but not send it
        for rec in self.records:
            self.assertEqual(rec.edi_exchange_state, "new")
        self.backend._cron_check_output_exchange_sync(skip_send=True)
        for rec in self.records:
            self.assertEqual(rec.edi_exchange_state, "output_pending")
            self.assertTrue(
                self.ExecutionAbstractModel.check_called_for(rec, "generate")
            )
            self.assertEqual(
                rec._get_file_content(), self.ExecutionAbstractModel._call_key(rec)
            )
            # TODO: test better?
            self.assertFalse(rec.ack_exchange_id)

    @mute_logger(*LOGGERS)
    def test_exchange_generate_new_auto_send(self):
        self.exchange_type_out.exchange_file_auto_generate = True
        # No content ready to be sent, will get the content and send it
        for rec in self.records:
            self.assertEqual(rec.edi_exchange_state, "new")
        self.backend._cron_check_output_exchange_sync()
        for rec in self.records:
            self.assertEqual(rec.edi_exchange_state, "output_sent")
            self.assertTrue(
                self.ExecutionAbstractModel.check_called_for(rec, "generate")
            )
            self.assertEqual(
                rec._get_file_content(), self.ExecutionAbstractModel._call_key(rec)
            )
            self.assertTrue(self.ExecutionAbstractModel.check_called_for(rec, "send"))

    @mute_logger(*LOGGERS)
    def test_exchange_generate_output_ready_auto_send(self):
        # No content ready to be sent, will get the content and send it
        self.exchange_type_out.check_model_id = self.model
        for rec in self.records:
            self.assertEqual(rec.edi_exchange_state, "new")
        self.record1._set_file_content("READY")
        self.record1.edi_exchange_state = "output_sent"
        self.backend.with_context(
            fake_update_values={"edi_exchange_state": "output_sent_and_processed"}
        )._cron_check_output_exchange_sync(skip_sent=False)
        for rec in self.records - self.record1:
            self.assertEqual(rec.edi_exchange_state, "new")
        self.assertEqual(self.record1.edi_exchange_state, "output_sent_and_processed")
        self.assertTrue(
            self.ExecutionAbstractModel.check_not_called_for(self.record1, "generate")
        )
        self.assertTrue(
            self.ExecutionAbstractModel.check_not_called_for(self.record1, "send")
        )
        self.assertTrue(
            self.ExecutionAbstractModel.check_called_for(self.record1, "check")
        )
