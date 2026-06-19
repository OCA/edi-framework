# Copyright 2026 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.edi_core_oca.tests.common import EDIBackendCommonTestCase


class EDIQueueCommonTestCase(EDIBackendCommonTestCase):
    def _make_record(self):
        return self.backend.create_record(
            "test_csv_input",
            {"model": self.partner._name, "res_id": self.partner.id},
        )

    def _get_delayed(self, record):
        delayed = record.with_context(queue_job__no_delay=False).with_delay()
        # Suppress "prepared but never delayed" warning
        # `Delayable Delayable(edi.exchange.record*) was prepared but never delayed`
        delayed.delayable._generated_job = object()
        return delayed
