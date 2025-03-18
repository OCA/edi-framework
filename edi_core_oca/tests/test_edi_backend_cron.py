# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tools import mute_logger

from .common import EDIBackendCommonTestCase

LOGGERS = ("odoo.addons.edi_core_oca.models.edi_backend", "odoo.addons.queue_job.delay")


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

    @mute_logger(*LOGGERS)
    def test_exchange_generate_new_no_auto(self):
        # No content ready to be sent, no auto-generate, nothing happens
        for rec in self.records:
            self.assertEqual(rec.edi_exchange_state, "new")
        self.backend._cron_check_output_exchange_sync()
        for rec in self.records:
            self.assertEqual(rec.edi_exchange_state, "new")
