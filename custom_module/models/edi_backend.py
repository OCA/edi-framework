# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class EDIBackend(models.Model):
    _inherit = "edi.backend"

    backend_group_id = fields.Many2one(
        string="EDI Backend group",
        comodel_name="edi.backend.group",
        ondelete="restrict",
    )

