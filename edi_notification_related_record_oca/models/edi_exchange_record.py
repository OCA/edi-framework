# Copyright 2026 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class EDIExchangeRecord(models.Model):
    _inherit = "edi.exchange.record"

    def _notify_related_record(self, message, level="info", action=None):
        records = self
        if action:
            records = self.filtered(
                lambda rec: rec.type_id._notify_related_record_on(action)
            )
        if not records:
            return
        return super(EDIExchangeRecord, records)._notify_related_record(
            message, level=level, action=action
        )
