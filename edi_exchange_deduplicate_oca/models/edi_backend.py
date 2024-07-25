# Copyright 2024 Camptocamp
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class EDIBackend(models.Model):

    _inherit = "edi.backend"

    def _failed_output_check_send_msg(self):
        return "Nothing to do. Likely already sent or obsolete."

    def _cron_delete_obsolete_records(self, **kw):
        for backend in self:
            backend._delete_obsolete_records(**kw)

    def _delete_obsolete_records(self, record_ids=None, **kw):
        """Cleanup obsolete records.

        Go through types with `delete_obsolete_records` flag on
        and delete their obsolete records if any.
        """
        obsolete_records = self.exchange_record_model.search(
            self._obsolete_records_domain(record_ids=record_ids)
        )
        _logger.info(
            "EDI Exchange delete records: found %d obsolete records to delete.",
            len(obsolete_records),
        )
        if obsolete_records:
            obsolete_records.unlink()

    def _obsolete_records_domain(self, record_ids=None):
        """
        Domain for obsolete records need to delete.
        If the record is obsolete, delete it even if the type's flag has been disabled.
        """
        domain = [
            ("backend_id", "=", self.id),
            ("edi_exchange_state", "=", "obsolete"),
        ]
        if record_ids:
            domain.append(("id", "in", record_ids))
        return domain
