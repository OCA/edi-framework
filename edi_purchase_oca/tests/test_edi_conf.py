# Copyright 2024 CamptoCamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo.addons.edi_oca.tests.common import EDIBackendCommonComponentTestCase


class TestsPurchaseEDIConfiguration(EDIBackendCommonComponentTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.purchase_order = cls.env["purchase.order"]
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "default_code": "1234567",
            }
        )
        cls.exc_type_out = cls.env.ref("edi_purchase_oca.demo_edi_exc_type_order_out")
        cls.edi_conf = cls.env.ref("edi_purchase_oca.demo_edi_configuration_confirmed")
        cls.partner.edi_purchase_conf_ids = cls.edi_conf

    @mock.patch("odoo.addons.edi_oca.models.edi_backend.EDIBackend._validate_data")
    @mock.patch("odoo.addons.edi_oca.models.edi_backend.EDIBackend._exchange_generate")
    @mock.patch("odoo.addons.edi_oca.models.edi_backend.EDIBackend._exchange_send")
    def test_order_confirm(self, mock_send, mock_generate, mock_validate):
        mock_generate.return_value = "TEST PO OUT"
        order = self.purchase_order.create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_qty": 10,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        self.assertEqual(order.state, "draft")
        self.assertEqual(len(order.exchange_record_ids), 0)
        order.button_confirm()
        self.assertEqual(order.state, "purchase")
        self.assertEqual(len(order.exchange_record_ids), 1)
        self.assertEqual(order.exchange_record_ids[0].type_id, self.exc_type_out)
        self.assertEqual(
            order.exchange_record_ids[0]._get_file_content(), "TEST PO OUT"
        )
