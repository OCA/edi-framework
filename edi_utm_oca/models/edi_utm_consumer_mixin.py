# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class EdiUtmConsumerMixin(models.AbstractModel):
    """Provide EDI source id for related records."""

    _name = "edi.utm.consumer.mixin"
    _description = __doc__

    edi_source_id = fields.Many2one("utm.source")

    def _edi_update_source(self, vals):
        if vals.get("origin_exchange_record_id"):
            exchange_record = self.env["edi.exchange.record"].browse(
                vals["origin_exchange_record_id"]
            )

            exchange_type = exchange_record.type_id

            if exchange_type.edi_source_id and "edi_source_id" not in vals:
                vals["edi_source_id"] = exchange_type.edi_source_id.id

        return vals
