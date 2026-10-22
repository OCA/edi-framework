# Copyright 2020 ACSONE
# Copyright 2021 Camptocamp
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo.orm.model_classes import add_to_registry
from odoo.tests import tagged

from odoo.addons.edi_core_oca.tests.common import EDIBackendCommonTestCase
from odoo.addons.queue_job.tests.common import trap_jobs


@tagged("-at_install", "post_install")
class EDIBackendTestOutputJobsCase(EDIBackendCommonTestCase):
    @classmethod
    def _setup_records(cls):  # pylint:disable=missing-return
        super()._setup_records()
        from odoo.addons.edi_core_oca.tests.fake_models import EdiTestExecution

        add_to_registry(cls.registry, EdiTestExecution)
        cls.registry._setup_models__(cls.env.cr, ["edi.framework.test.execution"])
        cls.registry.init_models(
            cls.env.cr, ["edi.framework.test.execution"], {"models_to_check": True}
        )
        cls.addClassCleanup(cls.registry.__delitem__, "edi.framework.test.execution")
        model = cls.env["ir.model"]._get("edi.framework.test.execution")
        cls.exchange_type_out.generate_model_id = model
        cls.exchange_type_out.send_model_id = model

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        vals = {
            "model": cls.partner._name,
            "res_id": cls.partner.id,
        }
        cls.record = cls.backend.create_record("test_csv_output", vals)
        cls.record.type_id.exchange_file_auto_generate = True

    @classmethod
    def _setup_context(cls):
        # Re-enable jobs
        return dict(super()._setup_context(), queue_job__no_delay=False)

    def test_job(self):
        with trap_jobs() as trap:
            self.backend._check_output_exchange_sync(record_ids=self.record.ids)
            trap.assert_jobs_count(2)
            trap.assert_enqueued_job(
                self.record.action_exchange_generate,
            )
            trap.assert_enqueued_job(
                self.record.action_exchange_send,
            )
            # No matter how many times we schedule jobs
            self.record.action_exchange_generate()
            self.record.action_exchange_generate()
            self.record.action_exchange_generate()
            # identity key should prevent having new jobs for same record
            trap.assert_jobs_count(2)
            # even if the content changed: the job reads it when it runs
            self.record._set_file_content("something different")
            self.record.action_exchange_generate()
            trap.assert_jobs_count(2)
            job = self.record.action_exchange_send()
            self.assertEqual(0, job.priority)
            trap.assert_jobs_count(2)

    def test_generate_send_chained(self):
        """Generating and sending a record queues one chain of two jobs.

        Scenario:
            1. Ask a new output record to be generated and sent.
            2. Run the queued jobs.
        Expected:
            - A generate job and a send job are queued.
            - The send job waits for the generate job and gets the top priority.
            - Once both ran, the record has been sent.
        """
        with trap_jobs() as trap:
            self.record.action_exchange_generate_send_chained()
            trap.assert_jobs_count(2)
            trap.assert_enqueued_job(self.record.action_exchange_generate)
            trap.assert_enqueued_job(
                self.record.action_exchange_send, properties={"priority": 0}
            )
            generate_job, send_job = sorted(
                trap.enqueued_jobs, key=lambda job: job.method_name
            )
            self.assertEqual(send_job.depends_on, {generate_job})
            trap.perform_enqueued_jobs()
        self.assertRecordValues(self.record, [{"edi_exchange_state": "output_sent"}])

    def test_generate_send_chained_then_sync(self):
        """The output sync does not queue a second send for a chained record.

        Scenario:
            1. Ask a new output record to be generated and sent.
            2. Generate its file, while the send job is still waiting.
            3. Run the output sync.
        Expected:
            - Only the send job queued with the generation exists.
        """
        self.record.action_exchange_generate_send_chained()
        self.record._set_file_content("something")
        self.record.edi_exchange_state = "output_pending"
        self.backend._check_output_exchange_sync(record_ids=self.record.ids)
        send_jobs = self.env["queue.job"].search(
            [("func_string", "=", f"{self.record}.action_exchange_send()")]
        )
        self.assertEqual(len(send_jobs), 1)
