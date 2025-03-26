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
        result = super().notify_action_complete(action, message=message)
        # Trigger generic action complete event on exchange record
        event_name = f"{action}_complete"
        self._trigger_edi_event(event_name)
        if self.related_record_exists:
            # Trigger specific event on related record
            self._trigger_edi_event(event_name, target=self.record)
        return result

    def _trigger_edi_event(self, name, suffix=None, target=None, **kw):
        """Trigger a component event linked to this backend and edi exchange."""
        name = self._trigger_edi_event_make_name(name, suffix=suffix)
        target = target or self
        target._event(name).notify(self, **kw)

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
        result = super()._notify_done()
        self._trigger_edi_event("done")
        return result

    def _notify_error(self, message_key):
        result = super()._notify_error(message_key)
        self._trigger_edi_event("error")
        return result

    def _notify_ack_received(self):
        result = super()._notify_ack_received()
        self._trigger_edi_event("done", suffix="ack_received")
        return result

    def _notify_ack_missing(self):
        result = super()._notify_ack_missing()
        self._trigger_edi_event("done", suffix="ack_missing")
        return result

    def _notify_ack_received_error(self):
        result = super()._notify_ack_received_error()
        self._trigger_edi_event("done", suffix="ack_received_error")
        return result
