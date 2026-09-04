# Copyright 2024 Camptocamp
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tools import mute_logger

from odoo.addons.edi_oca.tests.test_edi_backend_cron import EDIBackendTestCronCase

LOGGERS = ("odoo.addons.edi_oca.models.edi_backend", "odoo.addons.queue_job.delay")


class EDIBackendTestCronDeduplicationCase(EDIBackendTestCronCase):
    @mute_logger(*LOGGERS)
    def test_exchange_delete_obsolete_records(self):
        self.exchange_type_out.write(
            {
                "exchange_file_auto_generate": True,
                "deduplicate_on_send": True,
                "delete_obsolete_records": True,
            }
        )
        record1_1 = self.backend.create_record(
            "test_csv_output", {"model": self.partner._name, "res_id": self.partner.id}
        )
        record1_2 = self.backend.create_record(
            "test_csv_output", {"model": self.partner._name, "res_id": self.partner.id}
        )
        record1_3 = self.backend.create_record(
            "test_csv_output", {"model": self.partner._name, "res_id": self.partner.id}
        )
        # all the older records should have been obsolete by record1_3
        records = self.record1 + record1_1 + record1_2
        self.backend._check_output_exchange_sync()
        for record in records:
            self.assertEqual(record.edi_exchange_state, "obsolete")
        self.assertEqual(record1_3.edi_exchange_state, "output_sent")
        self.backend._delete_obsolete_records()
        for record in records:
            self.assertFalse(record.exists())
        self.assertTrue(record1_3.exists())
