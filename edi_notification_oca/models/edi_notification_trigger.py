# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class EDINotificationTrigger(models.Model):
    _name = "edi.notification.trigger"
    _description = "EDI Notification Trigger"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(
        required=True,
        copy=False,
        help="Exchange status the trigger reacts to, as passed to "
        "`edi.exchange.record._notify_state` (eg: 'send_ok', 'process_ko').",
    )
    sequence = fields.Integer(default=10)
    direction = fields.Selection(
        selection=[("input", "Input"), ("output", "Output"), ("both", "Both")],
        required=True,
        default="both",
        help="Direction of the exchange types the status can happen on.",
    )
    is_error = fields.Boolean(
        help="The status is an error. Its note is always posted on the related "
        "records, so it can only be used by activity rules.",
    )

    _sql_constraints = [("code_uniq", "unique(code)", "Code must be unique")]

    def _get_by_code(self, code):
        return self.search([("code", "=", code)], limit=1)
