# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from markupsafe import Markup

from odoo import models


class GS1GenerateInstructionMixin(models.AbstractModel):
    """Common ``generate`` handler for GS1 warehousing instructions.

    Replaces the old ``edi.exchange.template.output`` records: the work
    context (formerly built in the ``code_snippet``) and the QWeb
    rendering (formerly driven by the template ``code``) are now produced
    here and the result is returned to the EDI backend as the output.
    """

    _name = "edi.gs1.generate.instruction.mixin"
    _inherit = ["edi.oca.handler.generate", "edi.gs1.output.shipment.mixin"]
    _description = "GS1 generate warehousing instruction mixin"

    # Full xmlid of the QWeb template to render, set on concrete handlers.
    _template_ref = None

    def generate(self, exchange_record):
        work_ctx = self._get_work_ctx(exchange_record)
        work_ctx["info"] = self.generate_info(exchange_record, **work_ctx)
        # Some optional template branches rely on a falsy `TODO` flag.
        work_ctx.setdefault("TODO", False)
        # The business header gets its own parameters per document
        # (see ``_business_header_params``), hence a dedicated rendering
        # injected via ``t-out`` where the XSD expects it.
        work_ctx["business_header"] = Markup(
            self._render_edi_template(
                exchange_record,
                "edi_gs1_oca.edi_exchange_business_header",
                **self._business_header_params(work_ctx),
            )
        )
        return self._render_edi_template(
            exchange_record, self._template_ref, **work_ctx
        )

    def _get_work_ctx(self, exchange_record):
        """Build the partners context used by the QWeb template."""
        raise NotImplementedError()

    def _business_header_params(self, work_ctx):
        """Values passed to the GS1 business header template."""
        return {
            "sender": work_ctx["sender"],
            "receiver": work_ctx["receiver"],
        }

    def _get_shipper_partner(self, exchange_record):
        """Return the shipper (carrier) partner.

        The original module read ``record.carrier_id.partner_id``, but
        ``carrier_id`` is provided by ``stock_delivery`` (not a hard
        dependency) and the core ``delivery.carrier`` model has no
        ``partner_id`` field. We keep that source when available (e.g.
        ``stock_delivery`` installed and ``delivery.carrier`` extended with a
        partner) and fall back to the backend LSP partner otherwise.
        """
        record = exchange_record.record
        carrier = record.carrier_id if "carrier_id" in record._fields else None
        if carrier and "partner_id" in carrier._fields and carrier.partner_id:
            return carrier.partner_id
        return exchange_record.backend_id.lsp_partner_id


class GS1GenerateOutboundInstruction(models.AbstractModel):
    """Generate data for Outbound Instruction.

    The Warehousing Outbound Instruction message enables a Logistic
    Services Client (LSC) to inform his Logistic Services Provider (LSP)
    that goods will be shipped.
    """

    _name = "edi.gs1.generate.outbound.instruction"
    _inherit = "edi.gs1.generate.instruction.mixin"
    _description = "GS1 generate Warehousing Outbound Instruction"

    _template_ref = "edi_gs1_stock_oca.edi_exchange_outbound_instruction"

    def _business_header_params(self, work_ctx):
        return {
            "sender": work_ctx["sender"],
            "receiver": work_ctx["ls_seller"],
            "doc_type": "Warehousing Outbound Instruction",
        }

    def _get_work_ctx(self, exchange_record):
        backend = exchange_record.backend_id
        record = exchange_record.record
        sender = backend.lsc_partner_id
        return {
            "sender": sender,
            "receiver": record.partner_id,
            "ls_seller": backend.lsp_partner_id,
            "ls_buyer": sender,
            # FIXME: this is probably wrong or not always true
            "buyer": record.partner_id,
            # TODO: Pick the SO partner customer.
            "seller": backend.lsc_partner_id,
            # TODO: get a default carrier somehow?
            "shipper": self._get_shipper_partner(exchange_record),
            "shipto": record.partner_id,
        }

    def _generate_info(self, exchange_record, **kw):
        data = {
            "creationDateTime": self._utc_now(),
            # status code can stay always as it is if we don't send around copies
            "documentStatusCode": "ORIGINAL",
            "documentActionCode": self._document_action_code(),
            # fmt: off
            "warehousingOutboundInstructionShipment": self._shipment_info(
                exchange_record, **kw
            ),
            # fmt: on
        }
        return {"warehousingOutboundInstruction": data}

    def _shipment_info_elements(self):
        res = super()._shipment_info_elements()
        res.update(
            {
                "warehousingDespatchTypeCode": self._despatch_type_code,
                "plannedDespatch": self._planned_despatch,
            }
        )
        return res

    def _despatch_type_code(self, exchange_record, **kw):
        """TODO get it from picking or mapping configuration or leave

        CROSS-DOCKED_SHIPMENT
            Cross-docked shipment
            One on one cross-dock of an incoming cross-dock shipment.
        WAREHOUSE_CROSS-DOCK_COMBINATION
            Warehouse cross-dock combination
            combination of goods picked from stock
            and goods taken from cross-docked receipts.
        WAREHOUSE_SHIPMENT
            Warehouse shipment.
            All goods are picked from stock.
        """
        return "WAREHOUSE_SHIPMENT"

    def _planned_despatch(self, exchange_record, **kw):
        # TODO: better info from?
        values = {}
        record = exchange_record.record
        if record.scheduled_date:
            values.update(
                {
                    "logisticEventPeriod": {
                        "beginDate": self.date_to_string(record.scheduled_date),
                    },
                }
            )
        return values


class GS1GenerateInboundInstruction(models.AbstractModel):
    """Generate data for Inbound Instruction.

    The Warehousing Inbound Instruction message enables a Logistic
    Services Client (LSC) to inform his Logistic Services Provider (LSP)
    that goods will be arriving.
    """

    _name = "edi.gs1.generate.inbound.instruction"
    _inherit = "edi.gs1.generate.instruction.mixin"
    _description = "GS1 generate Warehousing Inbound Instruction"

    _template_ref = "edi_gs1_stock_oca.edi_exchange_inbound_instruction"

    def _get_work_ctx(self, exchange_record):
        backend = exchange_record.backend_id
        record = exchange_record.record
        sender = backend.lsc_partner_id
        receiver = backend.lsp_partner_id
        return {
            "sender": sender,
            "receiver": receiver,
            "ls_seller": receiver,
            "ls_buyer": sender,
            # FIXME: this is probably wrong or not always true
            "buyer": sender,
            "seller": record.purchase_id.partner_id,
            "shipper": self._get_shipper_partner(exchange_record),
        }

    def _generate_info(self, exchange_record, **kw):
        data = {
            "creationDateTime": self._utc_now(),
            # status code can stay always as it is if we don't send around copies
            "documentStatusCode": "ORIGINAL",
            "documentActionCode": self._document_action_code(),
            # fmt: off
            "warehousingInboundInstructionShipment": self._shipment_info(
                exchange_record, **kw
            ),
            # fmt: on
        }
        return {"warehousingInboundInstruction": data}

    def _shipment_info_elements(self):
        res = super()._shipment_info_elements()
        res.update(
            {
                "warehousingReceiptTypeCode": self._receipt_type_code,
                "plannedReceipt": self._planned_receipt,
            }
        )
        return res

    def _receipt_type_code(self, exchange_record, **kw):
        """TODO

        # cross-dock receipt.
        # The instructed receipt is intended to be cross-docked.
        "CROSS-DOCK_RECEIPT",
        # priority receipt.
        # The instructed receipt needs to be processed with high priority.
        "PRIORITY_RECEIPT",
        # regular receipt Normal receipt, no special actions required.
        "REGULAR_RECEIPT",
        # repair receipt.
        # The instructed receipt relates to goods that were under repair.
        "REPAIR_RECEIPT",
        # return
        # The instructed receipt is a return, for example a customer return or a recall.
        "RETURNS",
        """
        return "REGULAR_RECEIPT"

    def _planned_receipt(self, exchange_record, **kw):
        # TODO: better info from?
        return {
            "logisticEventDateTime": {
                "date": self.date_to_string(exchange_record.record.scheduled_date)
                or "",
            },
        }


class GS1ProcessOutboundNotification(models.AbstractModel):
    """Process data for Outbound Notification.

    The Warehousing Outbound Notification message enables a Logistic
    Services Provider (LSP) to inform his Logistic Services Client (LSC)
    on the status of goods received on behalf of the client.
    """

    _name = "edi.gs1.process.outbound.notification"
    _inherit = ["edi.oca.handler.process", "edi.gs1.input.shipment.mixin"]
    _description = "GS1 process Warehousing Outbound Notification"

    def process(self, exchange_record):
        data = self._parse(exchange_record)
        self._process_data(data, exchange_record)
        return self.env._("warehousingOutboundNotification processed")

    def _process_data(self, data, exchange_record):
        # TODO
        raise NotImplementedError()


class GS1ProcessInboundNotification(models.AbstractModel):
    """Process data for Inbound Notification.

    The Warehousing Inbound Notification message enables a Logistic
    Services Provider (LSP) to inform his Logistic Services Client (LSC)
    on the status of goods received on behalf of the client.
    """

    _name = "edi.gs1.process.inbound.notification"
    _inherit = ["edi.oca.handler.process", "edi.gs1.input.shipment.mixin"]
    _description = "GS1 process Warehousing Inbound Notification"

    def process(self, exchange_record):
        data = self._parse(exchange_record)
        self._process_data(data, exchange_record)
        return self.env._("warehousingInboundNotification processed")

    def _process_data(self, data, exchange_record):
        # TODO
        raise NotImplementedError()
