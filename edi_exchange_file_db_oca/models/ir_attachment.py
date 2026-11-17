# Copyright 2026 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    @api.model
    def _storage(self):
        if self.env.context.get("edi_exchange_file_content_in_db"):
            return "db"
        return super()._storage()
