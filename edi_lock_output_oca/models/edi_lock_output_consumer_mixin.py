# Copyright 2026 Camptocamp SA
# @author Akim Juillerat <akim.juillerat@camptocamp.com>
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models
from odoo.exceptions import ValidationError

LOCKED_STATES = ("output_sent", "output_sent_and_processed", "output_sent_and_error")


class EDILockOutputConsumerMixin(models.AbstractModel):
    """Lock fields of records once their EDI output was sent."""

    _name = "edi.lock.output.consumer.mixin"
    _description = "Lock fields of records once their EDI output was sent"

    def _edi_lock_output_fields(self):
        """Return the names of the fields locked once the record is sent."""
        return []

    def _edi_lock_output_is_locked(self):
        """Return the records of `self` that are locked.

        By default, a record is locked once an output exchange of a type
        flagged `lock_record_on_send` was sent for it. Overrides add their own
        locked records to the result of `super()`, never replace it.
        """
        groups = (
            self.env["edi.exchange.record"]
            .sudo()
            ._read_group(
                [
                    ("model", "=", self._name),
                    ("res_id", "in", self.ids),
                    ("type_id.direction", "=", "output"),
                    ("type_id.lock_record_on_send", "=", True),
                    ("edi_exchange_state", "in", LOCKED_STATES),
                ],
                groupby=["res_id"],
            )
        )
        return self.browse([res_id for (res_id,) in groups])

    def _edi_lock_output_bypass(self):
        """Tell whether the lock is bypassed, by context or by group."""
        return bool(
            self.env.context.get("edi_lock_output_bypass")
            or self.env.user.has_group("edi_lock_output_oca.group_bypass_lock")
        )

    def _edi_lock_output_message(self):
        """Return the error raised when a locked field is changed."""
        return self.env._("This record is locked because it has already been sent.")

    @api.constrains(lambda self: self._edi_lock_output_fields())
    def _edi_lock_output_check(self):
        """Refuse changes to the locked fields of locked records."""
        if not self._edi_lock_output_bypass() and self._edi_lock_output_is_locked():
            raise ValidationError(self._edi_lock_output_message())
