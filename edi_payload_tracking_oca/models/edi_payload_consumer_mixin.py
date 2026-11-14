# Copyright 2026 Camptocamp SA
# @author Akim Juillerat <akim.juillerat@camptocamp.com>
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class EDIPayloadConsumerMixin(models.AbstractModel):
    """Read and write the payload exported for a record."""

    _name = "edi.payload.consumer.mixin"
    _description = "EDI exported payload consumer mixin"

    def edi_payload_get_output(self):
        """Return the payload stored for this record, or an empty dict."""
        self.ensure_one()
        return self.env["edi.payload.output"].get_payload(self)

    def edi_payload_set_output(self, payload):
        """Store `payload` for this record, replacing the previous one."""
        self.ensure_one()
        return self.env["edi.payload.output"].set_payload(self, payload)

    def _edi_payload_has_changes(self, payload):
        """Tell whether `payload` holds anything not exported yet.

        True when nothing was exported for this record, or when a key of
        `payload` holds a value different from the stored one.
        """
        self.ensure_one()
        exported = self.edi_payload_get_output()
        return not exported or not all(
            exported.get(key) == value for key, value in payload.items()
        )
