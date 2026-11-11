# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from logging import getLogger

from openupgradelib import openupgrade

from odoo import Command

_logger = getLogger(__name__)

# statuses edi_core_oca reports through _notify_error, the only ones the
# legacy activity reacted to
LEGACY_ERROR_CODES = ("validate_ko", "send_ko", "receive_ko", "process_ko")


def _get_legacy_notifications(env):
    """Exchange types notifying on process error, with activity type and targets."""
    if not openupgrade.column_exists(
        env.cr, "edi_exchange_type", "notify_on_process_error"
    ):
        return []
    env.cr.execute(
        """
        SELECT t.id,
            t.direction,
            t.notify_on_process_error_activity_type_id,
            ARRAY(
                SELECT res_groups_id FROM edi_exchange_type_res_groups_rel
                WHERE edi_exchange_type_id = t.id
            ),
            ARRAY(
                SELECT res_users_id FROM edi_exchange_type_res_users_rel
                WHERE edi_exchange_type_id = t.id
            )
        FROM edi_exchange_type t
        WHERE t.notify_on_process_error
            AND t.notify_on_process_error_activity_type_id IS NOT NULL
        """
    )
    return [row for row in env.cr.fetchall() if row[3] or row[4]]


@openupgrade.migrate()
def migrate(env, version):
    env["edi.exchange.type"].with_context(active_test=False).search(
        []
    )._create_default_notification_rules()
    Rule = env["edi.notification.rule"]
    for (
        type_id,
        direction,
        activity_type_id,
        group_ids,
        user_ids,
    ) in _get_legacy_notifications(env):
        triggers = Rule._get_allowed_triggers(direction, "activity").filtered(
            lambda trigger: trigger.code in LEGACY_ERROR_CODES
        )
        rule = Rule.create(
            {
                "name": "Activity on errors",
                "type_id": type_id,
                "notification_type": "activity",
                "trigger_ids": [Command.set(triggers.ids)],
                "activity_type_id": activity_type_id,
                "group_ids": [Command.set(group_ids)],
                "user_ids": [Command.set(user_ids)],
            }
        )
        _logger.info(
            "Exchange type %s: process error notification migrated to %s",
            type_id,
            rule,
        )
