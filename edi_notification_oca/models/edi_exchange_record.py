# Copyright 2024 Camptocamp SA
# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class EDIExchangeRecord(models.Model):
    _name = "edi.exchange.record"
    _inherit = ["edi.exchange.record", "mail.activity.mixin"]

    def _notify_state(self, key, message=None, level="info"):  # pylint: disable=missing-return
        trigger = self.env["edi.notification.trigger"].sudo()._get_by_code(key)
        for rec in self:
            rules = rec.type_id._get_notification_rules(key)
            if rec._must_notify_related_record(trigger, rules):
                super(EDIExchangeRecord, rec)._notify_state(
                    key, message=message, level=level
                )
            activity_rules = rules.filtered(
                lambda rule: rule.notification_type == "activity"
            )
            if activity_rules:
                activity_rules._schedule_activities(
                    rec, trigger, message or rec._exchange_status_message(key)
                )

    def _must_notify_related_record(self, trigger, rules):
        """Whether the note of `trigger` is posted on the related records.

        Error notes, and notes of statuses without a trigger, are always
        posted.
        """
        self.ensure_one()
        if not trigger or trigger.is_error:
            return True
        return any(rule.notification_type == "message" for rule in rules)
