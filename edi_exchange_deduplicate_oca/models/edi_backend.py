# Copyright 2024 Camptocamp
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class EDIBackend(models.Model):
    _inherit = "edi.backend"

    def _failed_output_check_send_msg(self):
        return "Nothing to do. Likely already sent or obsolete."
