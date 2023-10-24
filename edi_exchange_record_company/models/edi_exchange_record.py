# Copyright 2023 ForgeFlow
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class EDIExchangeRecord(models.Model):
    _inherit = "edi.exchange.record"

    company_id = fields.Many2one("res.company", string="Company", readonly=True)
