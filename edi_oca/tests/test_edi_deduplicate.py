# Copyright 2024 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .common import EDIBackendCommonComponentRegistryTestCase
from .fake_components import (
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
        cls.record1 = cls.backend.create_record(
            "test_csv_output",
            {
                "model": cls.partner._name,
                "res_id": cls.partner.id,
            },
        )
        cls.record2 = cls.backend.create_record(
            "test_csv_output",
            {
                "model": cls.partner._name,
                "res_id": cls.partner.id,
            },
        )
        cls.record3 = cls.backend.create_record(
            "test_csv_output",
            {
                "model": cls.partner._name,
                "res_id": cls.partner.id,
            },
        )
        cls.record4 = cls.backend.create_record(
            "test_csv_output",
            {
                "model": cls.partner._name,
                "res_id": cls.partner.id,
            },
        )
        cls.records = cls.record1 + cls.record1 + cls.record3 + cls.record4

    def setUp(self):
        super().setUp()
        FakeOutputGenerator.reset_faked()
        FakeOutputSender.reset_faked()
        FakeOutputChecker.reset_faked()
        FakeInputProcess.reset_faked()

    def test_no_deduplicate_on_send(self):
        self.exchange_type_out.write(
            {
                "deduplicate_on_send": False,
            }
        )
        self.backend._check_output_exchange_sync()
        # All the records should be "output_sent"
        for record in self.records:
            self.assertEqual(record.edi_exchange_state, "output_sent")

    def test_deduplicate_on_send(self):
        self.exchange_type_out.write(
            {
                "deduplicate_on_send": True,
            }
        )
        self.backend._check_output_exchange_sync()
        # Because we just sent the last record, so the others should be "obsolete"
        self.records = self.records - self.record4
        for record in self.records:
            self.assertEqual(record.edi_exchange_state, "obsolete")
        self.assertEqual(self.record4.edi_exchange_state, "output_sent")
