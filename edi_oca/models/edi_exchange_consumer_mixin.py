# Copyright 2020 ACSONE SA
# Copyright 2020 Creu Blanca
# Copyright 2022 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import models


class EDIExchangeConsumerMixin(models.AbstractModel):
    _inherit = "edi.exchange.consumer.mixin"

    def edi_create_exchange_record(self, exchange_type_id):
        action = super().edi_create_exchange_record(exchange_type_id)
        exchange_type = self.env["edi.exchange.type"].browse(exchange_type_id)
        backend = exchange_type.backend_id
        domain = [("backend_type_id", "=", exchange_type.backend_type_id.id)]
        if not backend and self.env["edi.backend"].search_count(domain) == 1:
            backend = self.env["edi.backend"].search(domain)
            # FIXME: here you can still have more than one backend per type.
            # We should always get to the wizard w/ pre-populated values.
            # Maybe this behavior can be controlled by exc type adv param.
        if backend:
            exchange_record = self._edi_create_exchange_record(exchange_type, backend)
            self._event("on_edi_generate_manual").notify(self, exchange_record)
            return exchange_record.get_formview_action()
        return action
