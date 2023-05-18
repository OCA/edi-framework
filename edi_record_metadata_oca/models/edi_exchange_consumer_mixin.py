# Copyright 2023 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class EDIMetadataConsumerMixin(models.AbstractModel):
    """Add API to handle EDI stored metadata to exchange consumers."""

    _inherit = "edi.exchange.consumer.mixin"

    @api.model_create_multi
    def create(self, vals_list):
        do_store_metadata = self.env.context.get("edi_framework_action")
        if do_store_metadata:
            # Default create machinert will pollute values: let's freeze them.
            orig_vals = [vals.copy() for vals in vals_list]
        records = super().create(vals_list)
        if do_store_metadata:
            for rec, vals in zip(records, orig_vals):
                metadata = rec._edi_get_metadata_to_store(vals)
                if metadata:
                    rec._edi_store_metadata(metadata)
        return records

    def _edi_get_metadata_to_store(self, orig_vals):
        """Hook here to customize which values will be stored.

        :param `orig_vals`: values received by `create` method.
        """
        return {}

    def _edi_store_metadata(self, metadata):
        if self.origin_exchange_record_id:
            self.origin_exchange_record_id.set_metadata(metadata)

    def _edi_get_metadata(self):
        return self.origin_exchange_record_id.get_metadata()
