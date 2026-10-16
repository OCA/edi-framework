# Copyright 2024 Camptocamp SA
# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import Command, api, fields, models


class EDIExchangeType(models.Model):
    _inherit = "edi.exchange.type"

    notification_rule_ids = fields.One2many(
        string="Notification Rules",
        comodel_name="edi.notification.rule",
        inverse_name="type_id",
        help="Notes on the related records are posted only for the statuses of "
        "the active 'Note on related records' rules. Error notes are always "
        "posted.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        exchange_types = super().create(vals_list)
        if self.env.context.get("edi_notification_skip_default_rule"):
            return exchange_types
        exchange_types.filtered(
            lambda exc_type: not exc_type.notification_rule_ids.filtered(
                lambda rule: rule.notification_type == "message"
            )
        )._create_default_notification_rules()
        return exchange_types

    def _create_default_notification_rules(self):
        """Create the rule posting the note of every non-error status.

        It reproduces the notes `edi_core_oca` posts without this module.
        """
        Rule = self.env["edi.notification.rule"]
        return Rule.create(
            [
                {
                    "name": self.env._("Notes on related records"),
                    "type_id": exc_type.id,
                    "notification_type": "message",
                    "trigger_ids": [
                        Command.set(
                            Rule._get_allowed_triggers(
                                exc_type.direction, "message"
                            ).ids
                        )
                    ],
                }
                for exc_type in self
            ]
        )

    def _get_notification_rules(self, code):
        """Active notification rules of the exchange type reacting to `code`."""
        self.ensure_one()
        return self.sudo().notification_rule_ids.filtered(
            lambda rule: code in rule.trigger_ids.mapped("code")
        )
