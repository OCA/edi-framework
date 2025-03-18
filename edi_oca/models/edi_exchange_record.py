# Copyright 2020 ACSONE SA
# Copyright 2021 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class EDIExchangeRecord(models.Model):
    _inherit = "edi.exchange.record"

    def notify_action_complete(self, action, message=None):
        """Notify current record that an edi action has been completed.

        Implementers should take care of calling this method
        if they work on records w/o calling edi_backend methods (eg: action_send).

        Implementers can hook to this method to do something after any action ends.
        """
        if message:
            self._notify_related_record(message)

        # Trigger generic action complete event on exchange record
        event_name = f"{action}_complete"
        self._trigger_edi_event(event_name)
        if self.related_record_exists:
            # Trigger specific event on related record
            self._trigger_edi_event(event_name, target=self.record)

    def _notify_related_record(self, message, level="info"):
        """Post notification on the original record."""
        if not self.related_record_exists or not hasattr(
            self.record, "message_post_with_source"
        ):
            return
        self.record.message_post_with_source(
            "edi_core_oca.message_edi_exchange_link",
            render_values={
                "backend": self.backend_id,
                "exchange_record": self,
                "message": message,
                "level": level,
            },
            subtype_id=self.env.ref("mail.mt_note").id,
        )

    def _trigger_edi_event_make_name(self, name, suffix=None):
        return "on_edi_exchange_{name}{suffix}".format(
            name=name,
            suffix=("_" + suffix) if suffix else "",
        )

    def _trigger_edi_event(self, name, suffix=None, target=None, **kw):
        """Trigger a component event linked to this backend and edi exchange."""
        name = self._trigger_edi_event_make_name(name, suffix=suffix)
        target = target or self
        target._event(name).notify(self, **kw)

    def _notify_done(self):
        self._notify_related_record(self._exchange_status_message("process_ok"))
        self._trigger_edi_event("done")

    def _notify_error(self, message_key):
        self._notify_related_record(
            self._exchange_status_message(message_key),
            level="error",
        )
        self._trigger_edi_event("error")

    def _notify_ack_received(self):
        self._notify_related_record(self._exchange_status_message("ack_received"))
        self._trigger_edi_event("done", suffix="ack_received")

    def _notify_ack_missing(self):
        self._notify_related_record(
            self._exchange_status_message("ack_missing"),
            level="warning",
        )
        self._trigger_edi_event("done", suffix="ack_missing")

    def _notify_ack_received_error(self):
        self._notify_related_record(
            self._exchange_status_message("ack_received_error"),
        )
        self._trigger_edi_event("done", suffix="ack_received_error")
