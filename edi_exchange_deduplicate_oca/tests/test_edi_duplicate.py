# Copyright 2024 Camptocamp
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo_test_helper import FakeModelLoader

from odoo.tools import mute_logger

from odoo.addons.edi_core_oca.tests.common import EDIBackendCommonTestCase

LOGGERS = (
    "odoo.addons.edi_core_oca.models.edi_backend",
    "odoo.addons.queue_job.delay",
)


class EDIDeduplicateTestCase(EDIBackendCommonTestCase):
    def setUp(self):
        super().setUp()
        self.loader = FakeModelLoader(self.env, self.__module__)
        self.loader.backup_registry()
        from odoo.addons.edi_core_oca.tests.fake_models import EdiTestExecution

        self.loader.update_registry((EdiTestExecution,))
        self.model = self.env["ir.model"].search(
            [("model", "=", "edi.framework.test.execution")]
        )
        self.exchange_type_out.write(
            {
                "exchange_file_auto_generate": True,
                "generate_model_id": self.model.id,
                "send_model_id": self.model.id,
                "output_validate_model_id": self.model.id,
            }
        )

    def tearDown(self):
        self.loader.restore_registry()
        super().tearDown()

    @mute_logger(*LOGGERS)
    def test_deduplicate_on_send(self):
        self.exchange_type_out.write(
            {
                "deduplicate_on_send": True,
            }
        )
        record1 = self.backend.create_record(
            "test_csv_output",
            {
                "model": self.partner._name,
                "res_id": self.partner.id,
            },
        )
        record2 = self.backend.create_record(
            "test_csv_output",
            {
                "model": self.partner._name,
                "res_id": self.partner.id,
            },
        )
        record3 = self.backend.create_record(
            "test_csv_output",
            {
                "model": self.partner._name,
                "res_id": self.partner.id,
            },
        )
        records = record1 + record2
        self.backend._check_output_exchange_sync()
        # Because we just sent the last record, so the others should be "obsolete"
        for record in records:
            self.assertEqual(record.edi_exchange_state, "cancelled")
        self.assertEqual(record3.edi_exchange_state, "output_sent")

    @mute_logger(*LOGGERS)
    def test_no_deduplicate_on_send(self):
        self.exchange_type_out.write(
            {
                "deduplicate_on_send": False,
            }
        )
        record1 = self.backend.create_record(
            "test_csv_output",
            {
                "model": self.partner._name,
                "res_id": self.partner.id,
            },
        )
        record2 = self.backend.create_record(
            "test_csv_output",
            {
                "model": self.partner._name,
                "res_id": self.partner.id,
            },
        )
        record3 = self.backend.create_record(
            "test_csv_output",
            {
                "model": self.partner._name,
                "res_id": self.partner.id,
            },
        )
        records = record1 + record2 + record3
        self.backend._check_output_exchange_sync()
        # All the records should be "output_sent"
        for record in records:
            self.assertEqual(record.edi_exchange_state, "output_sent")

    @mute_logger(*LOGGERS)
    def test_block_obsolescence(self):
        self.exchange_type_out.write(
            {
                "deduplicate_on_send": True,
            }
        )
        record1 = self.backend.create_record(
            "test_csv_output",
            {
                "model": self.partner._name,
                "res_id": self.partner.id,
            },
        )
        record2 = self.backend.create_record(
            "test_csv_output",
            {
                "model": self.partner._name,
                "res_id": self.partner.id,
                # Checking
                "block_obsolescence": True,
            },
        )
        record3 = self.backend.create_record(
            "test_csv_output",
            {
                "model": self.partner._name,
                "res_id": self.partner.id,
            },
        )
        self.backend._check_output_exchange_sync()
        # Normally, record2 has been "obsolete"
        # But with block_obsolescence = True, it will be "output_sent" too
        self.assertEqual(record1.edi_exchange_state, "cancelled")
        self.assertEqual(record2.edi_exchange_state, "output_sent")
        self.assertEqual(record3.edi_exchange_state, "output_sent")
