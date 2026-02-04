# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import ast

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class EdiExchangeType(models.Model):
    _name = "edi.exchange.type"
    _inherit = ["edi.exchange.type", "mail.alias.mixin"]

    mail_as_attachment = fields.Boolean(
        string="Import Email as an Attachment",
    )

    @api.constrains("direction", "alias_domain_id", "alias_name")
    def _check_mail_configuration(self):
        for record in self:
            if record.direction != "input" and record.alias_email:
                raise ValidationError(
                    self.env._(
                        "You cannot have a receiving email for a non-incoming type."
                    )
                )

    def _alias_get_creation_values(self):
        values = super()._alias_get_creation_values()
        values["alias_model_id"] = self.env["ir.model"]._get("edi.exchange.record").id
        if self.id:
            values["alias_defaults"] = defaults = ast.literal_eval(
                self.alias_defaults or "{}"
            )
            defaults["backend_id"] = self.backend_id.id
            defaults["type_id"] = self.id
        return values
