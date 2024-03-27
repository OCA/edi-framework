# Copyright 2024 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import models


class EDIExchangeRecord(models.Model):

    _name = "edi.exchange.record"
    _inherit = ["edi.exchange.record", "mail.activity.mixin"]
