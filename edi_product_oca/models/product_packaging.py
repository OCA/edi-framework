# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductPackaging(models.Model):
    _name = "product.packaging"
    _inherit = ["product.packaging", "edi.exchange.consumer.mixin"]
