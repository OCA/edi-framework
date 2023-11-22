# Copyright 2023 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class EDIExchangeRelatedRecord(models.Model):
    """
    Model linking an Odoo record with an exchange record.
    """

    _name = "edi.exchange.related.record"
    _description = "EDI exchange Related Record"
    _order = "id"

    exchange_record_id = fields.Many2one(
        comodel_name="edi.exchange.record",
        required=True,
        ondelete="cascade",
        index=True,
    )
    model = fields.Char(index=True, required=True, readonly=True)
    res_id = fields.Many2oneReference(
        string="Record",
        index=True,
        required=True,
        readonly=True,
        model_field="model",
        copy=False,
    )

    _sql_constraints = [
        (
            "related_record_unique",
            "unique(exchange_record_id, model, res_id)",
            "A record can only be related once to a specific exchange record.",
        )
    ]

    @property
    def record(self):
        return self.env[self.model].browse(self.res_id).exists()

    def _notify_related_record(self, message, level="info"):
        """Post notification on the original record."""
        if not self.record or not hasattr(self.record, "message_post_with_view"):
            return
        self.record.message_post_with_view(
            "edi_oca.message_edi_exchange_link",
            values={
                "backend": self.exchange_record_id.backend_id,
                "exchange_record": self.exchange_record_id,
                "message": message,
                "level": level,
            },
            subtype_id=self.env.ref("mail.mt_note").id,
        )

    def action_open_related_record(self):
        self.ensure_one()
        if not self.record:
            return {}
        return self.record.get_formview_action()
