# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import models
from odoo.exceptions import UserError
from odoo.fields import Domain

_logger = logging.getLogger(__name__)


# TODO: inherit from exchange consumer


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _gs1_backend_domain(self):
        """Domain resolving the GS1 backend that serves this delivery.

        The backend is the one whose Logistic Services Provider runs the
        warehouse the delivery comes from, and whose Logistic Services Client
        is the company. Override to follow another convention.
        """
        self.ensure_one()
        warehouse = self.picking_type_id.warehouse_id
        if not warehouse.partner_id:
            # Without an LSP, `lsp_partner_id = False` would match any
            # backend left unconfigured.
            return Domain.FALSE
        return Domain.AND(
            [
                [
                    ("backend_type_id.code", "=", "gs1"),
                    ("lsp_partner_id", "=", warehouse.partner_id.id),
                    ("lsc_partner_id", "=", self.company_id.partner_id.id),
                ],
                Domain.OR(
                    [
                        [("company_id", "=", self.company_id.id)],
                        [("company_id", "=", False)],
                    ]
                ),
            ]
        )

    def get_backend_by_delivery(self):
        """Retrieve the GS1 backend for this delivery, empty when none fits."""
        self.ensure_one()
        return self.env["edi.backend"].search(self._gs1_backend_domain(), limit=1)

    def _common_instruction(self, send, type_code):
        delivery = self
        edi_backend = self.get_backend_by_delivery()
        if not edi_backend:
            raise UserError(
                self.env._(
                    "No GS1 backend serves %(name)s: check the logistic "
                    "services provider set on its warehouse.",
                    name=delivery.name,
                )
            )
        values = {"model": delivery._name, "res_id": delivery.id}
        exchange_record = edi_backend.create_record(type_code, values)
        edi_backend.exchange_generate(exchange_record)
        send = self.env.context.get("edi_exchange_send", send)
        if send:
            edi_backend.exchange_send(exchange_record)
        return exchange_record

    # TODO: check if sending is required
    def send_wh_inbound_instruction(self, send=False):
        """Generate an Inbound Instruction for given delivery and send it."""
        type_code = "warehousingInboundInstruction"
        return self._common_instruction(send, type_code)

    def action_send_wh_inbound_instruction(self):
        # TODO: return action compat dict
        return self.send_wh_inbound_instruction()

    def send_wh_outbound_instruction(self, send=False):
        """Generate an Outbound Instruction for given delivery and send it."""
        type_code = "warehousingOutboundInstruction"
        return self._common_instruction(send, type_code)

    def action_send_wh_outbound_instruction(self):
        # TODO: return action compat dict
        return self.send_wh_outbound_instruction()

    def action_stop_gs1(self):
        exchange_records = self.env["edi.exchange.record"].search(
            [("model", "=", self._name), ("res_id", "in", self.ids)]
        )
        if exchange_records:
            exchange_records.action_archive()
        return {}

    def unlink(self):
        """

        :return: bool
        """
        picking_ids = self.ids
        result = super().unlink()
        exchange_records = (
            self.env["edi.exchange.record"]
            .with_context(active_test=False)
            .search([("model", "=", self._name), ("res_id", "in", picking_ids)])
        )
        exchange_records.write({"model": False, "res_id": False})
        if exchange_records:
            exchange_records.action_archive()
        for exchange_record in exchange_records:
            exchange_record.message_post(body=self.env._("Related picking deleted"))
        return result
