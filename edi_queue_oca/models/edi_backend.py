# Copyright 2020 ACSONE SA
# Copyright 2021 Camptocamp
# Copyright 2025 Dixmit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from datetime import timedelta

from odoo import fields, models

from odoo.addons.queue_job.exception import RetryableJobError
from odoo.addons.queue_job.job import (
    CANCELLED,
    DONE,
    ENQUEUED,
    PENDING,
    STARTED,
    WAIT_DEPENDENCIES,
)

_logger = logging.getLogger(__name__)

# States a parent job can still leave on its own to unblock its dependents.
LIVE_JOB_STATES = (PENDING, ENQUEUED, STARTED, WAIT_DEPENDENCIES)


class EDIBackend(models.Model):
    _inherit = "edi.backend"

    def _send_retryable_exceptions(self):
        # IOError is a base class for all connection errors
        # OSError is a base class for all errors
        # when dealing w/ internal or external systems or filesystems
        return (IOError, OSError)

    def _retryable_exception(self):
        return RetryableJobError

    def _job_gc_stale_grace_hours(self):
        """Return the delay before a stranded job is collected.

        The grace period leaves time to requeue the failed parent by hand,
        which brings its dependents back to life on its own.
        """
        param = self.env["ir.config_parameter"].sudo()
        return int(param.get_param("edi_queue_oca.gc_stale_jobs_grace_hours", 24))

    def _job_gc_stale_domain(self, grace_hours):
        deadline = fields.Datetime.now() - timedelta(hours=grace_hours)
        return [
            ("model_name", "=", self.exchange_record_model._name),
            ("state", "=", WAIT_DEPENDENCIES),
            ("date_created", "<=", deadline),
        ]

    def _job_gc_is_stale(self, job, parent_states):
        parent_uuids = (job.dependencies or {}).get("depends_on") or []
        if not parent_uuids:
            return False
        # A parent missing from the mapping has been vacuumed away: nothing
        # will ever wake this job up again.
        blocking = [
            parent_states.get(uuid)
            for uuid in parent_uuids
            if parent_states.get(uuid) != DONE
        ]
        return bool(blocking) and not any(x in LIVE_JOB_STATES for x in blocking)

    def _job_gc_stale_result(self):
        return self.env._(
            "Cancelled by the EDI garbage collector: "
            "no remaining parent job can ever resume it."
        )

    def _job_gc_stale(self):
        """Cancel exchange jobs that can never be woken up.

        ``queue_job`` cancels dependents only when a parent is explicitly
        cancelled: when a parent fails they stay in ``wait_dependencies``
        forever, as EDI retries spawn a brand new job graph.
        """
        job_model = self.env["queue.job"].sudo()
        candidates = job_model.search(
            self._job_gc_stale_domain(self._job_gc_stale_grace_hours())
        )
        if not candidates:
            return job_model.browse()
        parent_uuids = set()
        for job in candidates:
            parent_uuids.update((job.dependencies or {}).get("depends_on") or [])
        parent_states = {
            job.uuid: job.state
            for job in job_model.search([("uuid", "in", list(parent_uuids))])
        }
        stale = candidates.filtered(
            lambda job: self._job_gc_is_stale(job, parent_states)
        )
        if stale:
            _logger.info("EDI exchange GC: cancelling %d stale jobs.", len(stale))
            stale._change_job_state(CANCELLED, result=self._job_gc_stale_result())
        return stale
