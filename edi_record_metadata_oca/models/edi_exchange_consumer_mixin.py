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
            # If an origin record is already given at creation
            # let's store metadata immediately before the creation really happens.
            # This way, if you have logic relying on metadata to be present at create
            # you will be able to make it work.
            # If the origin is set later, you'll need to handle it by yourself.
            for vals in vals_list:
                origin_id = vals.get("origin_exchange_record_id")
                metadata = self._edi_get_metadata_to_store(vals)
                if origin_id and metadata:
                    self._edi_store_metadata_before_create(origin_id, metadata)
        return super().create(vals_list)

    @api.model
    def _edi_get_metadata_to_store(self, orig_vals):
        """Hook here to customize which values will be stored.

        :param `orig_vals`: values received by `create` method.
        """
        return {}

    def _edi_store_metadata(self, metadata):
        if self.origin_exchange_record_id:
            self.origin_exchange_record_id.set_metadata(metadata)

    @api.model
    def _edi_store_metadata_before_create(self, origin_id, metadata):
        self.env["edi.exchange.record"].browse(origin_id).set_metadata(metadata)

    def _edi_get_metadata(self):
        return self.origin_exchange_record_id.get_metadata()
