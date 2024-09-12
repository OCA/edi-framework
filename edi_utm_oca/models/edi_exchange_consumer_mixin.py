# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, models


class EDIExchangeConsumerMixin(models.AbstractModel):
    _inherit = "edi.exchange.consumer.mixin"

    def _edi_get_utm_source(self):
        return self.env.ref(
            "edi_utm_oca.utm_source_edi",
            raise_if_not_found=False,
        )

    def _edi_update_source(self, vals):
        """Set UTM source for records created via EDI."""

        conditions = [
            "source_id" in self._fields,
            vals.get("origin_exchange_record_id"),
            "source_id" not in vals,
        ]

        if all(conditions):
            utm_source_edi = self._edi_get_utm_source()

            if utm_source_edi:
                vals["source_id"] = utm_source_edi.id

        return vals

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._edi_update_source(vals)
        return super().create(vals_list)
