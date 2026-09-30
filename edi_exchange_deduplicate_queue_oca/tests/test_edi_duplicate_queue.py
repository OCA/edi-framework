# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.edi_core_oca.tests.common import EDIBackendCommonTestCase
from odoo.addons.queue_job.tests.common import JobMixin


class TestEDIDeduplicateQueue(EDIBackendCommonTestCase, JobMixin):
    @classmethod
    def _setup_context(cls):
        return dict(super()._setup_context(), queue_job__no_delay=None)

    @classmethod
    def _setup_records(cls):  # pylint:disable=missing-return
        super()._setup_records()
        cls.exchange_type_out.deduplicate_on_exchange = True

    def _create_record(self, partner=None):
        partner = partner or self.partner
        return self.backend.create_record(
            "test_csv_output",
            {
                "model": partner._name,
                "res_id": partner.id,
            },
        )

    def test_obsolete_cancels_jobs(self):
        """The jobs of an obsolete record are cancelled, chained ones included.

        Scenario:
            1. Create a record and chain its generate and send jobs.
            2. Create a newer record for the same partner, with its own job.
        Expected:
            - The first record is obsolete and both its jobs are cancelled.
            - The job of the newer record is still pending.
        """
        record1 = self._create_record()
        job_counter = self.job_counter()
        record1.action_exchange_generate_send_chained()
        jobs1 = job_counter.search_created()
        self.assertEqual(len(jobs1), 2)
        self.assertEqual(
            sorted(jobs1.mapped("state")), ["pending", "wait_dependencies"]
        )
        record2 = self._create_record()
        job2 = record2.with_delay().action_exchange_generate().db_record()
        self.assertEqual(record1.edi_exchange_state, "obsolete")
        self.assertEqual(jobs1.mapped("state"), ["cancelled", "cancelled"])
        self.assertEqual(jobs1[0].result, "Exchange record is obsolete.")
        self.assertEqual(job2.state, "pending")

    def test_obsolete_keeps_started_jobs(self):
        """A job that already started is left alone."""
        record1 = self._create_record()
        job1 = record1.with_delay().action_exchange_generate().db_record()
        job1.state = "started"
        self._create_record()
        self.assertEqual(record1.edi_exchange_state, "obsolete")
        self.assertEqual(job1.state, "started")

    def test_other_records_jobs_untouched(self):
        """Only the jobs of the obsolete record are cancelled."""
        other_partner = self.env["res.partner"].create({"name": "EDI EXC OTHER"})
        other_record = self._create_record(other_partner)
        other_job = other_record.with_delay().action_exchange_generate().db_record()
        record1 = self._create_record()
        job1 = record1.with_delay().action_exchange_generate().db_record()
        self._create_record()
        self.assertEqual(record1.edi_exchange_state, "obsolete")
        self.assertEqual(job1.state, "cancelled")
        self.assertEqual(other_record.edi_exchange_state, "new")
        self.assertEqual(other_job.state, "pending")
