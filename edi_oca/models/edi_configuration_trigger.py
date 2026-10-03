# Copyright 2024 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class EdiConfigurationTrigger(models.Model):
    _name = "edi.configuration.trigger"
    _description = """
        Describe what triggers a specific action for a configuration.
    """

    name = fields.Char(required=True)
    code = fields.Char(required=True, copy=False)
    active = fields.Boolean(default=True)
    description = fields.Char(help="Describe what the conf is for")
    model_id = fields.Many2one(
        "ir.model",
        string="Model",
        help="Model the conf applies to. Leave blank to apply for all models",
    )

    _sql_constraints = [("code_uniq", "unique(code)", "Code must be unique")]
