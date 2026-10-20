# Copyright 2026 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import timedelta

from odoo.tests import tagged

from odoo.addons.queue_job.job import Job

from .common import EDIQueueCommonTestCase


@tagged("-at_install", "post_install")
class EDIBackendTestGCJobsCase(EDIQueueCommonTestCase):
    def _make_chained_jobs(self, parent_state, age_hours=0):
        record = self._make_record()
        parent = Job(record.action_exchange_receive)
        child = Job(record.action_exchange_process)
        child.add_depends({parent})
        parent.state = parent_state
        child.date_created -= timedelta(hours=age_hours)
        parent.store()
        child.store()
        return parent, child

    def _set_grace_hours(self, hours):
        self.env["ir.config_parameter"].sudo().set_param(
            "edi_queue_oca.gc_stale_jobs_grace_hours", hours
        )

    def test_gc_stale_exchange_jobs(self):
        pending_parent, live_child = self._make_chained_jobs("pending", age_hours=25)
        failed_parent, stale_child = self._make_chained_jobs("failed", age_hours=25)
        self.assertEqual(live_child.db_record().state, "wait_dependencies")
        self.assertEqual(stale_child.db_record().state, "wait_dependencies")
        self._set_grace_hours(48)
        self.assertFalse(self.backend._job_gc_stale())
        self.assertEqual(stale_child.db_record().state, "wait_dependencies")
        self._set_grace_hours(24)
        collected = self.backend._job_gc_stale()
        self.assertEqual(collected, stale_child.db_record())
        self.assertEqual(stale_child.db_record().state, "cancelled")
        self.assertEqual(
            stale_child.db_record().result, self.backend._job_gc_stale_result()
        )
        self.assertEqual(live_child.db_record().state, "wait_dependencies")
        self.assertEqual(failed_parent.db_record().state, "failed")
        self.assertEqual(pending_parent.db_record().state, "pending")
