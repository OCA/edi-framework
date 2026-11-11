# Copyright 2024 Camptocamp
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.edi_oca.tests.common import EDIBackendCommonComponentRegistryTestCase
from odoo.addons.edi_oca.tests.fake_components import (
    FakeInputProcess,
    FakeOutputChecker,
    FakeOutputGenerator,
    FakeOutputSender,
)

LOGGERS = ("odoo.addons.edi_oca.models.edi_backend", "odoo.addons.queue_job.delay")


class EDIDeduplicateTestCase(EDIBackendCommonComponentRegistryTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._build_components(
            cls,
            FakeOutputGenerator,
            FakeOutputSender,
            FakeOutputChecker,
            FakeInputProcess,
        )
        cls.partner = cls.env.ref("base.res_partner_10")
        cls.exchange_type_out.exchange_file_auto_generate = True

    def setUp(self):
        super().setUp()
        FakeOutputGenerator.reset_faked()
        FakeOutputSender.reset_faked()
        FakeOutputChecker.reset_faked()
        FakeInputProcess.reset_faked()

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
            self.assertEqual(record.edi_exchange_state, "obsolete")
        self.assertEqual(record3.edi_exchange_state, "output_sent")

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
        self.assertEqual(record1.edi_exchange_state, "obsolete")
        self.assertEqual(record2.edi_exchange_state, "output_sent")
        self.assertEqual(record3.edi_exchange_state, "output_sent")
