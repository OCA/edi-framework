# Copyright 2020 Dixmit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ["account.move", "edi.exchange.consumer.mixin"]
