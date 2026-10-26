# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class GS1InputShipmentMessageMixin(models.AbstractModel):
    """Common GS1 input shipment mixin.

    Replaces the old ``edi.gs1.input.shipment.mixin`` component.
    Concrete processors inherit this mixin together with
    ``edi.oca.handler.process``.
    """

    _name = "edi.gs1.input.shipment.mixin"
    _inherit = "edi.gs1.input.mixin"
    _description = "GS1 EDI input shipment mixin"

    def _process_data(self, data, exchange_record):
        # TODO
        pass
