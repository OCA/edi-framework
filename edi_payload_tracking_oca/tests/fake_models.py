# Copyright 2026 Camptocamp SA
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class EDIPayloadConsumerTest(models.Model):
    """Record whose exported payload is tracked, for tests only."""

    _name = "edi.payload.consumer.test"
    _inherit = ["edi.payload.consumer.mixin"]
    _description = "Model used only for test"

    name = fields.Char()
