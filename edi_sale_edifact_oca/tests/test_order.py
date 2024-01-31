# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions

from odoo.addons.edi_oca.tests.common import EDIBackendCommonComponentRegistryTestCase

from .common import OrderInboundTestMixin


class TestOrderInbound(
    EDIBackendCommonComponentRegistryTestCase, OrderInboundTestMixin
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend = cls._get_backend()
        cls._setup_inbound_order(cls.backend)

    @classmethod
    def _get_backend(cls):
        return cls.env.ref("edi_edifact_oca.edi_backend_edifact_demo")

    def test_new_order(self):
        self.exc_record_in.action_exchange_process()
        self.assertEqual(self.exc_record_in.edi_exchange_state, "input_processed")
        order = self.exc_record_in.record
        self.assertEqual(order.partner_id, self.order_data["partner"])
        self.assertEqual(order.client_order_ref, self.order_data["client_order_ref"])
        self.assertEqual(order.partner_shipping_id, self.order_data["shipping_partner"])

        order_msg = order.message_ids[0]
        self.assertIn("Exchange processed successfully", order_msg.body)
        self.assertIn(self.exc_record_in.identifier, order_msg.body)
        order.env.invalidate_all()
        # Test relations
        self.assertEqual(len(order.exchange_record_ids), 1)
        exc_record = order.exchange_record_ids.filtered(
            lambda x: x.type_id == self.exc_type_in
        )
        self.assertEqual(exc_record, self.exc_record_in)

    def test_existing_order_break_on_error(self):
        self.assertEqual(self.exc_record_in.edi_exchange_state, "input_received")
        self.env["sale.order"].create(
            {
                "partner_id": self.env.ref(
                    "sale_order_import_edifact.partner_edi_dm"
                ).id,
                "client_order_ref": self.order_data["client_order_ref"],
            }
        )
        with self.assertRaisesRegex(
            exceptions.UserError, self.err_msg_already_imported
        ):
            self.exc_record_in.with_context(
                _edi_process_break_on_error=True
            ).action_exchange_process()
        self.assertEqual(self.exc_record_in.edi_exchange_state, "input_received")

    def test_existing_order(self):
        self.assertEqual(self.exc_record_in.edi_exchange_state, "input_received")
        self.env["sale.order"].create(
            {
                "partner_id": self.env.ref(
                    "sale_order_import_edifact.partner_edi_dm"
                ).id,
                "client_order_ref": self.order_data["client_order_ref"],
            }
        )
        # Test w/ error handling
        self.exc_record_in.action_exchange_process()
        self.assertEqual(self.exc_record_in.edi_exchange_state, "input_processed_error")
        err_msg = "Sales order has already been imported before"
        self.assertIn(err_msg, self.exc_record_in.exchange_error)
