# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductBarcode(models.Model):
    _name = "product.barcode"
    _inherit = ["product.barcode", "edi.exchange.consumer.mixin"]
