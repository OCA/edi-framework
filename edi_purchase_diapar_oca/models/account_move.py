# Copyright (C) 2016-Today: Druidoo (<http://www.druidoo.net/>)
# @author: Druidoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    partner_is_edi = fields.Boolean(
        related="partner_id.is_edi",
        string="Partner (Is Edi)",
        store=True,
    )
