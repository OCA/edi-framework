# Copyright 2026 Camptocamp SA
# @author Akim Juillerat <akim.juillerat@camptocamp.com>
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import json

from odoo import models


class EDIBackend(models.Model):
    _inherit = "edi.backend"

    def _output_check_send(self, exchange_record):
        res = super()._output_check_send(exchange_record)
        return res and not self._deduplicate_payload_unchanged(exchange_record)

    def exchange_send(self, exchange_record):
        """Send exchange file."""
        # The docstring repeats the original one: queue_job uses it as the
        # description of the send jobs.
        # A record with nothing new to send must not stay pending: the output
        # cron would keep queuing a send job for it, forever.
        if super()._output_check_send(
            exchange_record
        ) and self._deduplicate_payload_unchanged(exchange_record):
            exchange_record.edi_exchange_state = "obsolete"
            return self._deduplicate_payload_unchanged_msg()
        return super().exchange_send(exchange_record)

    def _deduplicate_payload_unchanged_msg(self):
        """Return the result of a send skipped because nothing changed."""
        return "Nothing to send: payload already exported. Marked as obsolete."

    def _deduplicate_payload_unchanged(self, exchange_record):
        """Tell whether the payload holds nothing new for its record.

        Only for exchange types deduplicating unchanged payloads. True when
        the related record is gone; false when its model does not track its
        exported payload.
        """
        if not exchange_record.type_id.deduplicate_unchanged_payload:
            return False
        record = exchange_record.record
        if not record:
            return True
        if not hasattr(record, "_edi_payload_has_changes"):
            return False
        payload = json.loads(exchange_record._get_file_content())
        return not record._edi_payload_has_changes(payload)
