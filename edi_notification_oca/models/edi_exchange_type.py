# Copyright 2024 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import api, fields, models


class EDIExchangeType(models.Model):
    _inherit = "edi.exchange.type"

    notify_on_process_error = fields.Boolean(
        help="If an error happens on process, a notification will be sent to all"
        " selected users. If active, please select the specific groups and"
        " specific users in the 'Notifications' page.",
        default=False,
    )
    notify_on_process_error_groups_ids = fields.Many2many(
        comodel_name="res.groups",
        string="Notify Groups On Process Error",
        inverse="_inverse_notify_on_process_error_groups_users",
    )
    notify_on_process_error_users_ids = fields.Many2many(
        comodel_name="res.users",
        string="Notify Users On Process Error",
        inverse="_inverse_notify_on_process_error_groups_users",
        help="Select users to send notifications to. If 'Notification Groups' "
        "have been selected, notifications will also be sent to users selected in here.",
    )
    notify_on_process_error_activity_type_id = fields.Many2one(
        "mail.activity.type",
        string="Activity Type Used When Notify On Process Error",
        default=lambda self: self._default_notify_on_process_error_activity_type_id(),
    )

    def _default_notify_on_process_error_activity_type_id(self):
        return self.env.ref(
            "edi_notification_oca.mail_activity_failed_exchange_record_warning", False
        )

    @api.onchange("notify_on_process_error")
    def _onchange_notify_on_process_error(self):
        if not self.notify_on_process_error:
            self.notify_on_process_error_groups_ids = None
            self.notify_on_process_error_users_ids = None

    def _inverse_notify_on_process_error_groups_users(self):
        for rec in self:
            if (
                rec.notify_on_process_error_groups_ids
                or rec.notify_on_process_error_users_ids
            ):
                rec.notify_on_process_error = True
