# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_lsp = fields.Boolean(string="Is Logistic Services Provider (LSP)")

    def _gs1_gln(self):
        """Return the GLN of this partner.

        This addon stores no GLN: an integration module provides the source,
        be it a plain field or `partner_identification_gln`. Called on a
        single partner or on an empty recordset.
        """
        return ""
