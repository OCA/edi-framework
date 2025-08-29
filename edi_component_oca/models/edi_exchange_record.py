# Copyright 2025 Camptocamp
# Copyright 2025 Dixmit
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class EdiExchangeRecord(models.Model):
    _inherit = "edi.exchange.record"

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
        return super()._trigger_edi_event(name, suffix=suffix, target=target, **kw)
