# Copyright 2026 Camptocamp SA
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class EDIExchangeType(models.Model):
    _inherit = "edi.exchange.type"

    lock_record_on_send = fields.Boolean(
        string="Lock record on send",
        help="Once an exchange of this type is sent, the fields that its "
        "record declares as locked can no longer be changed, except by the "
        "users of the 'Bypass EDI output lock' group. Only records whose "
        "model uses the lock mixin are concerned.",
    )
