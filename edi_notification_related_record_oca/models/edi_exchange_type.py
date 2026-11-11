# Copyright 2026 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class EDIExchangeType(models.Model):
    _inherit = "edi.exchange.type"

    notify_related_record_on_generate = fields.Boolean(
        string="Notify related record on generate",
        default=True,
        help="Post a note on the related record when the exchange is generated.",
    )
    notify_related_record_on_send = fields.Boolean(
        string="Notify related record on send",
        default=True,
        help="Post a note on the related record when the exchange is sent.",
    )
    notify_related_record_on_process = fields.Boolean(
        string="Notify related record on process",
        default=True,
        help="Post a note on the related record when the exchange is processed, "
        "successfully or with errors. Applies to both directions, as each one "
        "has its own counterpart: an incoming exchange is processed by Odoo, "
        "whereas for an outgoing one it is the receiving party that reports "
        "back having processed it.",
    )
    notify_related_record_on_receive = fields.Boolean(
        string="Notify related record on receive",
        default=True,
        help="Post a note on the related record when the exchange is received.",
    )

    def _notify_related_record_on(self, action):
        """Whether a chatter note should be posted on the related record.

        Gated per action via the `notify_related_record_on_*` toggles. Actions
        without a dedicated toggle (eg: acknowledgements) keep notifying, to
        preserve the behavior of `edi_oca` alone.
        """
        self.ensure_one()
        field_name = "notify_related_record_on_%s" % action
        if field_name not in self._fields:
            return True
        return self[field_name]
