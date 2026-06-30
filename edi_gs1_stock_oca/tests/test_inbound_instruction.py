# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from .common import ShipmentTestCaseBase


class InboundInstructionTestCase(ShipmentTestCaseBase):
    _schema_path = (
        "edi_gs1_oca:static/schemas/gs1/ecom/WarehousingInboundInstruction.xsd"
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_order()
        cls.exc_type = cls.env.ref(
            "edi_gs1_stock_oca.edi_exchange_type_inbound_instruction"
        )
        cls.handler = cls.env["edi.gs1.generate.inbound.instruction"]
        vals = {
            "model": cls.delivery._name,
            "res_id": cls.delivery.id,
            "type_id": cls.exc_type.id,
        }
        cls.record = cls.backend.create_record(cls.exc_type.code, vals)

    def test_generator_wired(self):
        self.assertEqual(
            self.exc_type.generate_model_id.model,
            "edi.gs1.generate.inbound.instruction",
        )

    def test_work_ctx(self):
        values = self.handler._get_work_ctx(self.record)
        expected = [
            ("sender", self.backend.lsc_partner_id),
            ("receiver", self.backend.lsp_partner_id),
            ("ls_buyer", self.backend.lsc_partner_id),
            ("ls_seller", self.backend.lsp_partner_id),
            ("buyer", self.backend.lsc_partner_id),
            ("seller", self.purchase.partner_id),
        ]
        for k, v in expected:
            self.assertEqual(values[k], v)
        self.assertTrue(values["shipper"])

    @freeze_time("2020-07-09 10:30:00")
    def test_info_provider_data(self):
        work_ctx = self.handler._get_work_ctx(self.record)
        work_ctx["shipper"] = self.carrier
        expected_shipment = {
            "shipmentIdentification": {
                "additionalShipmentIdentification": {
                    "attrs": {
                        # fmt: off
                        "additionalShipmentIdentificationTypeCode": "GOODS_RECEIVER_ASSIGNED"  # noqa: E501
                        # fmt: on
                    },
                    "value": self.delivery.name,
                }
            },
            "shipper": {
                "gln_code": "0000000000123",
                "additionalPartyIdentification": {
                    "attrs": {
                        # fmt: off
                        "additionalPartyIdentificationTypeCode": "BUYER_ASSIGNED_IDENTIFIER_FOR_A_PARTY"  # noqa: E501
                        # fmt: on
                    },
                    "value": "CARRIER#1",
                },
            },
            "packageTotal": [
                {
                    "packageTypeCode": "AF",
                    "totalPackageQuantity": "2",
                    "totalGrossWeight": {
                        "value": self.delivery.weight,
                        "attrs": {"measurementUnitCode": "KGM"},
                    },
                }
            ],
            "warehousingReceiptTypeCode": "REGULAR_RECEIPT",
            "plannedReceipt": {"logisticEventDateTime": {"date": "2020-07-12"}},
            "_shipment_items": [
                {
                    "lineItemNumber": 1,
                    "note": {},
                    "transactionalTradeItem": {"gtin": "1" * 14},
                    "inventoryDutyFeeTaxStatus": [],
                    "_plannedQty": {
                        "value": 300.0,
                        "attrs": {"measurementUnitCode": "KGM"},
                    },
                },
                {
                    "lineItemNumber": 2,
                    "note": {},
                    "transactionalTradeItem": {"gtin": "2" * 14},
                    "inventoryDutyFeeTaxStatus": [],
                    "_plannedQty": {
                        "value": 200.0,
                        "attrs": {"measurementUnitCode": "KGM"},
                    },
                },
                {
                    "lineItemNumber": 3,
                    "note": {},
                    "transactionalTradeItem": {"gtin": "3" * 14},
                    "inventoryDutyFeeTaxStatus": [],
                    "_plannedQty": {
                        "value": 100.0,
                        "attrs": {"measurementUnitCode": "KGM"},
                    },
                },
            ],
        }
        info = self.handler.generate_info(
            self.record, **work_ctx
        ).warehousingInboundInstruction
        for k, v in expected_shipment.items():
            self.assertEqual(
                info.warehousingInboundInstructionShipment[k], v, f"{k} does not match"
            )

    @freeze_time("2020-07-09 10:30:00")
    def test_xml(self):
        record = self.delivery.with_context(
            edi_exchange_send=False
        ).action_send_wh_inbound_instruction()
        file_content = record._get_file_content()
        self.assertEqual(self._validate_xml(file_content), None)
