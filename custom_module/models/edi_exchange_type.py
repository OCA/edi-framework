# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class EDIExchangeType(models.Model):
    _inherit = "edi.exchange.type"

    exchange_type_group_id = fields.Many2one(
        string="EDI Exchange Type group",
        comodel_name="edi.exchange.type.group",
        ondelete="restrict",
    )
