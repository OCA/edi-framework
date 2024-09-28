# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class EDIExchangeTypeGroup(models.Model):
    """Define a kind of exchange type Group."""

    _name = "edi.exchange.type.group"
    _description = "EDI Exchange Type Group"

    name = fields.Char(required=True)

    _sql_constraints = [
        ("uniq_code", "unique(name)", "Exchange type group name must be unique!")
    ]
