# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models
from odoo.fields import Domain

from odoo.addons.queue_job.job import CANCELLED, ENQUEUED, PENDING, WAIT_DEPENDENCIES


class EdiExchangeRecord(models.Model):
    _inherit = "edi.exchange.record"

    def write(self, vals):
        res = super().write(vals)
        if vals.get("edi_exchange_state") == "obsolete":
            self._cancel_obsolete_jobs()
        return res

    def _cancel_obsolete_jobs(self):
        """Cancel the jobs of these records that have not started yet."""
        domain = self._get_related_queue_job_domain() & Domain(
            "state", "in", (WAIT_DEPENDENCIES, PENDING, ENQUEUED)
        )
        jobs = self.env["queue.job"].sudo().search(domain)
        jobs._change_job_state(
            CANCELLED, result=self.env._("Exchange record is obsolete.")
        )
