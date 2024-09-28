# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class EDIBackendGroup(models.Model):
    """Define a kind of backend Group."""

    _name = "edi.backend.group"
    _description = "EDI Backend Group"

    name = fields.Char(required=True)

    _sql_constraints = [
        ("uniq_code", "unique(name)", "Backend group name must be unique!")
    ]
