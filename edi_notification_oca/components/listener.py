# Copyright 2024 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _

from odoo.addons.component.core import Component


class EdiNotificationListener(Component):
    _name = "edi.notification.component.listener"
    _inherit = "base.event.listener"

    def on_edi_exchange_error(self, record):
        exc_type = record.type_id
        notify_on_process_error = exc_type.notify_on_process_error
        activity_type = exc_type.notify_on_process_error_activity_type_id
        if (
            not notify_on_process_error
            or not activity_type
            or not (
                exc_type.notify_on_process_error_groups_ids
                or exc_type.notify_on_process_error_users_ids
            )
        ):
            return True
        users = self._get_users_to_notify(exc_type)
        # Send notification to defined users
        for user in users:
            record.activity_schedule(
                activity_type_id=activity_type.id,
                summary=_(
                    "EDI: Process error on record '%(identifier)s'.",
                    identifier=record.identifier,
                ),
                note=record.exchange_error,
                user_id=user.id,
                automated=True,
            )
        return True

    def _get_users_to_notify(self, exc_type):
        exc_type.ensure_one()
        return (
            exc_type.notify_on_process_error_groups_ids.users
            | exc_type.notify_on_process_error_users_ids
        )
