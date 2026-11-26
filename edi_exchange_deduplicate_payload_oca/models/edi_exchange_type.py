# Copyright 2026 Camptocamp SA
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class EDIExchangeType(models.Model):
    _inherit = "edi.exchange.type"

    deduplicate_unchanged_payload = fields.Boolean(
        string="Deduplicate unchanged payloads",
        help="Do not send a payload holding nothing new compared with the "
        "payload exported for its record: the exchange is marked as obsolete "
        "instead. Only for records whose model tracks its exported payload "
        "(edi.payload.consumer.mixin). The payload must be a JSON object.",
    )
