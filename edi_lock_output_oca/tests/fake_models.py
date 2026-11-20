# Copyright 2026 Camptocamp SA
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class EDILockOutputConsumerTest(models.Model):
    """Record locked once sent, for tests only."""

    _name = "edi.lock.output.consumer.test"
    _inherit = ["edi.lock.output.consumer.mixin"]
    _description = "Model used only for test"

    name = fields.Char()
    qty = fields.Integer()
    note = fields.Char()

    def _edi_lock_output_fields(self):
        """Lock the name and the quantity."""
        return super()._edi_lock_output_fields() + ["name", "qty"]

    def _edi_lock_output_is_locked(self):
        """Lock the frozen records too."""
        # sudo: the test model has no access rights for plain users.
        return super()._edi_lock_output_is_locked() | self.filtered(
            lambda rec: rec.sudo().note == "frozen"
        )
