# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64

from odoo.addons.component.tests.common import TransactionComponentCase
from odoo.addons.edi_oca.tests.common import EDIBackendTestMixin


class TestProcessComponent(TransactionComponentCase, EDIBackendTestMixin):
    @classmethod
    def _get_backend(cls):
        return cls.env.ref("edi_edifact_oca.edi_backend_edifact_demo")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_env()
        cls.backend = cls._get_backend()
        cls.exc_type = cls.env.ref(
            "edi_account_edifact_oca.demo_edi_exc_type_edifact_invoice_out"
        )
        cls.company = cls.env.ref("base.main_company")
        cls.product1 = cls.env.ref("product.product_product_4")
        cls.product2 = cls.env.ref("product.product_product_1")
        cls.customer = cls.env.ref(
            "account_invoice_edifact.partner_edifact_invoiceto_dm"
        )
        cls.customer.write({"edi_account_move_out_exchange_type_id": cls.exc_type.id})
        cls.invoice = cls.env["account.move"].create(
            {
                "company_id": cls.company.id,
                "move_type": "out_invoice",
                "partner_id": cls.customer.id,
                "partner_shipping_id": cls.env.ref(
                    "account_invoice_edifact.partner_edifact_shipto_dm"
                ).id,
                "invoice_user_id": cls.env.ref(
                    "account_invoice_edifact.user_edifact_sender_dm"
                ).id,
                "currency_id": cls.company.currency_id.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product1.id,
                            "product_uom_id": cls.product1.uom_id.id,
                            "quantity": 12,
                            "price_unit": 42.42,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product2.id,
                            "product_uom_id": cls.product2.uom_id.id,
                            "quantity": 2,
                            "price_unit": 12.34,
                        },
                    ),
                ],
            }
        )

    def test_post_invoices(self):
        self.invoice.action_post()
        self.invoice.invalidate_model(fnames=["exchange_record_ids"])
        exchange_record = self.invoice.exchange_record_ids[0]
        self.assertEqual(len(exchange_record), 1)
        self.assertEqual(exchange_record.exchange_file, False)
        self.assertEqual(exchange_record.edi_exchange_state, "new")
        self.assertEqual(exchange_record.exchanged_on, False)

    def test_generate_file(self):
        self.invoice.action_post()
        self.invoice.invalidate_model(fnames=["exchange_record_ids"])
        exchange_record = self.invoice.exchange_record_ids[0]
        exchange_record.action_exchange_generate()
        self.assertNotEqual(exchange_record.exchange_file, False)
        self.assertEqual(exchange_record.edi_exchange_state, "output_pending")
        self.assertEqual(exchange_record.exchanged_on, False)

        # Compare data after generating
        expected_data = self.invoice.edifact_invoice_generate_data()
        self.assertEqual(
            exchange_record.exchange_file, base64.b64encode(expected_data.encode())
        )
