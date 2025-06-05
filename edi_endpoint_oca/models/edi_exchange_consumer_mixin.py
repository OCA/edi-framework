# Copyright 2023 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class EDIExchangeConsumerMixin(models.AbstractModel):
    _inherit = "edi.exchange.consumer.mixin"

    origin_edi_endpoint_id = fields.Many2one(
        string="EDI origin endpoint",
        comodel_name="edi.endpoint",
        ondelete="set null",
        # related="origin_exchange_record_id.edi_endpoint_id",
        # Do not use `related` here, as it would not work
        # in some environments where other models
        # are interfacing with this mixin
        # and the related field might not be available yet
        # when the registry is updated.
        compute="_compute_origin_edi_endpoint_id",
        compute_sudo=True,
        # Store it to ease searching
        store=True,
    )

    def _compute_origin_edi_endpoint_id(self):
        for rec in self:
            rec.origin_edi_endpoint_id = rec.origin_exchange_record_id.edi_endpoint_id
