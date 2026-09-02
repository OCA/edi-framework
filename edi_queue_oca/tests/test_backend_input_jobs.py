# Copyright 2026 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import tagged

from odoo.addons.queue_job.tests.common import trap_jobs

from .common import EDIQueueCommonTestCase


@tagged("-at_install", "post_install")
class EDIBackendTestInputJobsCase(EDIQueueCommonTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.record = cls.backend.create_record(
            "test_csv_input",
            {
                "model": cls.partner._name,
                "res_id": cls.partner.id,
                "edi_exchange_state": "input_pending",
            },
        )

    @classmethod
    def _setup_context(cls):
        # Re-enable jobs
        return dict(super()._setup_context(), queue_job__no_delay=False)

    def test_receive_process_chained(self):
        """Receiving and processing a record queues one chain of two jobs.

        Scenario:
            1. Ask a pending input record to be received and processed.
            2. Run the queued jobs.
        Expected:
            - A receive job and a process job are queued.
            - The process job waits for the receive job and gets the top priority.
            - Once both ran, the record has been processed.
        """
        with trap_jobs() as trap:
            self.record.action_exchange_receive_process_chained()
            trap.assert_jobs_count(2)
            trap.assert_enqueued_job(self.record.action_exchange_receive)
            trap.assert_enqueued_job(
                self.record.action_exchange_process, properties={"priority": 0}
            )
            process_job, receive_job = sorted(
                trap.enqueued_jobs, key=lambda job: job.method_name
            )
            self.assertEqual(process_job.depends_on, {receive_job})
            trap.perform_enqueued_jobs()
        self.assertRecordValues(
            self.record, [{"edi_exchange_state": "input_processed"}]
        )
