# Copyright 2020 ACSONE SA
# Copyright 2021 Camptocamp
# Copyright 2025 Dixmit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import models

from odoo.addons.queue_job.exception import RetryableJobError


class EDIBackend(models.Model):
    _inherit = "edi.backend"

    def _send_retryable_exceptions(self):
        # IOError is a base class for all connection errors
        # OSError is a base class for all errors
        # when dealing w/ internal or external systems or filesystems
        return (IOError, OSError)

    def _retryable_exception(self):
        return RetryableJobError
