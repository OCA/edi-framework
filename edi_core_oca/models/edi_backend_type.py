# Copyright 2020 ACSONE SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models

from ..utils import normalize_string


class EDIBackendType(models.Model):
    """Define a kind of backend."""

    _name = "edi.backend.type"
    _description = "EDI Backend Type"

    name = fields.Char(required=True)
    code = fields.Char(
        required=True,
        inverse="_inverse_code",
    )

    _sql_constraints = [
        ("uniq_code", "unique(code)", "Backend type code must be unique!")
    ]

    @api.onchange("name", "code")
    def _onchange_code(self):
        for rec in self:
            rec.code = rec.code or rec.name

    def _inverse_code(self):
        for rec in self:
            # Make sure it's always normalized
            rec.code = normalize_string(self, rec.code)

    def copy_data(self, default=None):
        # OVERRIDE: ``code`` cannot be copied as it must me unique.
        # Yet, we want to be able to duplicate a record from the UI.
        self.ensure_one()
        default = dict(default or {})
        default.setdefault("code", f"{self.code}/COPY_FIXME")
        return super().copy_data(default=default)
