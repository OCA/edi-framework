# Copyright 2020 Dixmit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EdiBackend(models.Model):
    _inherit = "edi.backend"

    webservice_backend_id = fields.Many2one("webservice.backend")
