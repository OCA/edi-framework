# Copyright 2026 Camptocamp SA
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models

from odoo.addons.queue_job.exception import RetryableJobError


class EDIPayloadOutput(models.Model):
    _inherit = "edi.payload.output"

    @api.model
    def _payload_concurrent_create_error(self, record, error):
        # Retry the job: next time, it finds the payload stored by the
        # concurrent job and merges its own on top of it.
        return RetryableJobError(
            f"The exported payload of {record} was created by a concurrent job."
        )
