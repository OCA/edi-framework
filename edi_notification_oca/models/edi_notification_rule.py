# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, exceptions, fields, models


class EDINotificationRule(models.Model):
    _name = "edi.notification.rule"
    _description = "EDI Notification Rule"
    _order = "sequence, id"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    type_id = fields.Many2one(
        string="Exchange Type",
        comodel_name="edi.exchange.type",
        required=True,
        ondelete="cascade",
        index=True,
    )
    notification_type = fields.Selection(
        selection=[
            ("message", "Note on related records"),
            ("activity", "Activity on exchange record"),
        ],
        required=True,
        default="message",
        help="Note on related records: post the status note on the records the "
        "exchange is related to. Error notes are always posted, so they are not "
        "available here.\n"
        "Activity on exchange record: schedule an activity on the exchange "
        "record for the selected users and the users of the selected groups.",
    )
    trigger_ids = fields.Many2many(
        string="Triggers",
        comodel_name="edi.notification.trigger",
        relation="edi_notification_rule_trigger_rel",
        column1="rule_id",
        column2="trigger_id",
        required=True,
        domain="[('id', 'in', allowed_trigger_ids)]",
        help="Exchange statuses the rule reacts to.",
    )
    allowed_trigger_ids = fields.Many2many(
        comodel_name="edi.notification.trigger",
        compute="_compute_allowed_trigger_ids",
    )
    activity_type_id = fields.Many2one(
        comodel_name="mail.activity.type",
        default=lambda self: self._default_activity_type_id(),
    )
    group_ids = fields.Many2many(
        string="Groups",
        comodel_name="res.groups",
        relation="edi_notification_rule_res_groups_rel",
        column1="rule_id",
        column2="group_id",
    )
    user_ids = fields.Many2many(
        string="Users",
        comodel_name="res.users",
        relation="edi_notification_rule_res_users_rel",
        column1="rule_id",
        column2="user_id",
    )

    def _default_activity_type_id(self):
        return self.env.ref(
            "edi_notification_oca.mail_activity_failed_exchange_record_warning", False
        )

    @api.model
    def _get_allowed_triggers(self, direction, notification_type):
        domain = [("direction", "in", [direction, "both"])]
        if notification_type == "message":
            domain.append(("is_error", "=", False))
        return self.env["edi.notification.trigger"].search(domain)

    @api.depends("type_id.direction", "notification_type")
    def _compute_allowed_trigger_ids(self):
        for rule in self:
            rule.allowed_trigger_ids = self._get_allowed_triggers(
                rule.type_id.direction, rule.notification_type
            )

    @api.constrains("type_id", "notification_type", "trigger_ids")
    def _check_trigger_ids(self):
        for rule in self:
            invalid = rule.trigger_ids - rule.allowed_trigger_ids
            if invalid:
                raise exceptions.ValidationError(
                    self.env._(
                        "Rule '%(name)s' cannot react to: %(triggers)s. Error "
                        "statuses always post their note, and a status must "
                        "match the direction of the exchange type.",
                        name=rule.name,
                        triggers=", ".join(invalid.mapped("name")),
                    )
                )

    @api.constrains("notification_type", "activity_type_id", "group_ids", "user_ids")
    def _check_activity_targets(self):
        for rule in self.filtered(lambda r: r.notification_type == "activity"):
            if not rule.activity_type_id or not (rule.group_ids or rule.user_ids):
                raise exceptions.ValidationError(
                    self.env._(
                        "Rule '%(name)s' schedules activities: it needs an "
                        "activity type and at least one user or group.",
                        name=rule.name,
                    )
                )

    def _get_activity_users(self):
        return self.group_ids.users | self.user_ids

    def _schedule_activities(self, exchange_record, trigger, message):
        note = exchange_record.exchange_error if trigger.is_error else message
        summary = self.env._(
            "EDI: %(trigger)s on record '%(identifier)s'.",
            trigger=trigger.name,
            identifier=exchange_record.identifier,
        )
        for rule in self:
            for user in rule._get_activity_users():
                exchange_record.activity_schedule(
                    activity_type_id=rule.activity_type_id.id,
                    summary=summary,
                    note=note,
                    user_id=user.id,
                    automated=True,
                )
