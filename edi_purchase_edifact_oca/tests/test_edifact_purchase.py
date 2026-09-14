# Copyright 2024 Trobz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import re
from base64 import b64encode

from odoo import fields

from odoo.addons.component.tests.common import TransactionComponentCase
from odoo.addons.edi_oca.tests.common import EDIBackendTestMixin


class TestEdifactPurchaseOrder(TransactionComponentCase, EDIBackendTestMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.base_edifact_model = cls.env["base.edifact"]
        cls.company = cls.env.ref("base.main_company")
        cls.product_1 = cls.env.ref("product.product_delivery_01")
        cls.product_2 = cls.env.ref("product.product_delivery_02")
        cls.product_3 = cls.env.ref("product.product_order_01")
        partner_id_number = cls.env["res.partner.id_number"]
        cls.partner_1 = cls.env.ref("base.res_partner_1")
        cls.partner_1.edifact_purchase_order_out = True
        cls.partner_2 = cls.env.ref("base.res_partner_12")
        cls.exc_type_input = cls.env.ref(
            "edi_purchase_edifact_oca.edi_exchange_type_purchase_order_input"
        )
        cls.edi_config_out_po = cls.env.ref(
            "edi_purchase_oca.demo_edi_configuration_confirmed"
        )
        cls.edi_config_out_po.write(
            {
                "backend_id": cls.env.ref(
                    "edi_purchase_edifact_oca.edi_backend_edifact"
                ),
                "type_id": cls.env.ref(
                    "edi_purchase_edifact_oca.edi_exchange_type_purchase_order_out"
                ),
            }
        )
        cls.partner_1.write(
            {"edi_purchase_conf_ids": [(6, 0, cls.edi_config_out_po.ids)]}
        )
        partner_id_number_data_1 = {
            "category_id": cls.env.ref(
                "partner_identification_gln.partner_identification_gln_number_category"
            ).id,
            "partner_id": cls.partner_1.id,
            "name": "9780201379624",
        }
        partner_id_number_data_2 = {
            "category_id": cls.env.ref(
                "partner_identification_gln.partner_identification_gln_number_category"
            ).id,
            "partner_id": cls.partner_2.id,
            "name": "9780201379174",
        }
        partner_id_number.create(partner_id_number_data_1)
        partner_id_number.create(partner_id_number_data_2)
        cls.env.user.partner_id = cls.partner_2
        cls.env.user.company_id.partner_id = cls.partner_2

        cls.datetime = fields.Datetime.now()
        cls.purchase = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner_1.id,
                "date_order": cls.datetime,
                "date_planned": cls.datetime,
            }
        )
        cls.po_line1 = cls.purchase.order_line.create(
            {
                "order_id": cls.purchase.id,
                "product_id": cls.product_1.id,
                "name": cls.product_1.name,
                "date_planned": cls.datetime,
                "product_qty": 12,
                "product_uom": cls.product_1.uom_id.id,
                "price_unit": 42.42,
            }
        )
        cls.po_line2 = cls.purchase.order_line.create(
            {
                "order_id": cls.purchase.id,
                "product_id": cls.product_2.id,
                "name": cls.product_2.name,
                "date_planned": cls.datetime,
                "product_qty": 2,
                "product_uom": cls.product_2.uom_id.id,
                "price_unit": 12.34,
            }
        )

    def test_edifact_purchase_generate_data(self):
        edifact_data = self.purchase.edifact_purchase_generate_data()
        self.assertTrue(edifact_data)
        self.assertEqual(isinstance(edifact_data, str), True)

    def test_edifact_purchase_get_interchange(self):
        interchange = self.purchase._edifact_purchase_get_interchange()
        self.assertEqual(interchange.sender, ["9780201379174", "14"])
        self.assertEqual(interchange.recipient, ["9780201379624", "14"])
        self.assertEqual(interchange.syntax_identifier, ["UNOC", "3"])

    def test_edifact_purchase_get_header(self):
        segments = self.purchase._edifact_purchase_get_header()
        seg = ("UNH", "", ["ORDERS", "D", "96A", "UN", "EAN008"])
        self.assertEqual(segments[0], seg)
        self.assertEqual(len(segments), 19)

    def test_edifact_purchase_get_product(self):
        segments, vals = self.purchase._edifact_purchase_get_product()
        self.assertEqual(len(segments), 22)
        self.assertEqual(len(vals), 2)

    def test_edifact_purchase_get_summary(self):
        vals = {"total_line_item": 2}
        segments = self.purchase._edifact_purchase_get_summary(vals)
        self.assertEqual(len(segments), 3)

    def test_edifact_purchase_get_address(self):
        partner = self.purchase.partner_id
        if hasattr(partner, "street3"):
            partner.street3 = "Address"
            self.assertEqual(
                self.purchase._edifact_purchase_get_address(partner), partner.street3
            )
        else:
            self.assertEqual(
                self.purchase._edifact_purchase_get_address(partner), partner.street
            )

    def test_action_confirm(self):
        self.purchase.button_confirm()
        self.assertEqual(self.purchase.exchange_record_count, 1)
        exchange_record = self.purchase.exchange_record_ids[0]
        exchange_record.backend_id.exchange_generate(exchange_record)
        file_content = exchange_record._get_file_content()
        self.assertTrue(file_content, "The generated file content should not be empty.")
        self.assertEqual(exchange_record.edi_exchange_state, "output_pending")
        self.assertEqual(exchange_record.exchanged_on, False)

        # Compare data after generating
        expected_data = self.purchase.edifact_purchase_generate_data()
        expected_data = expected_data.replace(
            "UNH++ORDERS", f"UNH+{exchange_record.id}+ORDERS"
        )
        # Add edi_exchange_record.id to UNT segment in expected_data
        pattern = r"(UNT\+[^']*\+)[^']*(?=(?:'|$))"
        expected_data = re.sub(
            pattern,
            lambda match: f"{match.group(1)}{exchange_record.id}",
            expected_data,
        )
        self.assertEqual(
            exchange_record.exchange_file, b64encode(expected_data.encode())
        )

    def test_edifact_purchase_wizard_import(self):
        self.partner_1.edifact_purchase_order_out = False
        edifact_data = self.purchase.edifact_purchase_generate_data()
        self.assertTrue(edifact_data)
        self.assertEqual(isinstance(edifact_data, str), True)
        self.purchase.button_confirm()
        edifact_data = edifact_data.replace("UNH++ORDERS", "UNH+1+DESADV")
        edifact_data = edifact_data.replace(
            "'UNS+S'",
            (
                "'LIN+3++:EN'PIA+1+FURN_9999:SA::91'PIA+1+FURN_9999:BP::92'"
                "QTY+21:4.0:'QTY+52::'DTM+2:20250110:102'MOA+203:0.0'PRI+AAA:0.0'"
                "PRI+AAB:0.0'RFF+PL:338'TAX+7+VAT+++:::0'UNS+S'"
            ),
        )
        wiz = self.env["purchase.order.import"].create(
            {
                "import_type": "edifact",
                "order_file": base64.b64encode(edifact_data.encode()),
                "order_filename": "test_edifact.txt",
            }
        )
        self.assertEqual(self.purchase.state, "purchase")
        # Import file to confirm purchase order
        wiz.import_order_button()

        new_order = self.env["purchase.order.line"].search(
            [("product_id.default_code", "=", self.product_3.default_code)]
        )

        self.assertTrue(new_order.order_id)
        self.assertEqual(new_order.move_ids.quantity, 4)

        sum_quantity_done = sum(self.purchase.order_line.mapped("move_ids.quantity"))
        self.assertEqual(sum_quantity_done, 14.0)

    def test_edifact_purchase_wizard_import_new_po(self):
        self.partner_1.edifact_purchase_order_out = False
        edifact_data = self.purchase.edifact_purchase_generate_data()
        self.assertTrue(edifact_data)
        self.assertEqual(isinstance(edifact_data, str), True)
        self.purchase.button_confirm()
        self.purchase.picking_ids.action_cancel()
        edifact_data = edifact_data.replace("UNH++ORDERS", "UNH+1+DESADV")

        wiz = self.env["purchase.order.import"].create(
            {
                "import_type": "edifact",
                "order_file": base64.b64encode(edifact_data.encode()),
                "order_filename": "test_edifact.txt",
            }
        )
        self.assertEqual(self.purchase.state, "purchase")
        # Import file to confirm purchase order
        action = wiz.import_order_button()

        new_order = self.env["purchase.order"].search([("id", "=", action["res_id"])])
        sum_quantity_done = sum(new_order.order_line.mapped("move_ids.quantity"))

        self.assertNotEqual(self.purchase.id, new_order.id)
        self.assertEqual(len(new_order.order_line), 2)
        self.assertEqual(sum_quantity_done, 14.0)

    def test_edifact_purchase_wizard_import_ignore_unknown(self):
        self.partner_1.edifact_purchase_order_out = False
        edifact_data = self.purchase.edifact_purchase_generate_data()
        self.assertTrue(edifact_data)
        self.assertEqual(isinstance(edifact_data, str), True)
        self.purchase.button_confirm()
        edifact_data = edifact_data.replace("UNH++ORDERS", "UNH+1+DESADV").replace(
            "LIN+1++:EN'PIA+1+FURN_7777:SA::91", "LIN+1++:EN'PIA+1+FURN_77778:SA::91"
        )

        wiz = self.env["purchase.order.import"].create(
            {
                "import_type": "edifact",
                "order_file": base64.b64encode(edifact_data.encode()),
                "order_filename": "test_edifact.txt",
            }
        )
        self.assertEqual(self.purchase.state, "purchase")
        # Import file to confirm purchase order
        wiz.import_order_button()

        sum_quantity_done = sum(self.purchase.order_line.mapped("move_ids.quantity"))
        self.assertEqual(sum_quantity_done, 2.0)

    def test_edifact_purchase_exchange_record_input(self):
        self.partner_1.edifact_purchase_order_out = False
        edifact_data = self.purchase.edifact_purchase_generate_data()
        self.assertTrue(edifact_data)
        self.assertEqual(isinstance(edifact_data, str), True)

        self.purchase.button_confirm()
        edifact_data = edifact_data.replace("UNH++ORDERS", "UNH+1+DESADV")
        edifact_data = edifact_data.replace(
            "'UNS+S'",  # noqa: E501
            (
                "'LIN+3++:EN'PIA+1+FURN_8888:SA::91'PIA+1+FURN_8888:BP::92'"
                "QTY+21:5.0:'QTY+52::'DTM+2:20250707:102'MOA+203:24.68'"
                "PRI+AAA:12.34'PRI+AAB:12.34'RFF+PL:35'TAX+7+VAT+++:::0'UNS+S'"
            ),
        )

        exchange_record_out = self.purchase.exchange_record_ids[0]
        exchange_record_out.backend_id.exchange_generate(exchange_record_out)

        exchange_record = self.env["edi.exchange.record"].create(
            {
                "backend_id": exchange_record_out.backend_id.id,
                "type_id": self.exc_type_input.id,
                "model": "purchase.order",
                "res_id": self.purchase.id,
            }
        )
        self.assertEqual(self.purchase.exchange_record_count, 2)

        exchange_record._set_file_content(edifact_data)
        exchange_record.write({"edi_exchange_state": "input_received"})
        exchange_record.backend_id.exchange_process(exchange_record)

        record = self.exc_type_input.backend_id.create_record(
            self.exc_type_input.code,
            {
                "edi_exchange_state": "input_received",
                "exchange_file": base64.b64encode(edifact_data.encode()),
            },
        )
        record.exchange_filename = "output-1.edi"
        self.assertEqual(self.purchase.state, "purchase")

        # Run `exchange_process`, It will run through the def `process` of
        # the component edi.input.process.edifact.input
        record.action_exchange_process()

        self.assertEqual(record.exchange_filename, "output-1.edi")
        self.assertEqual(record.res_id, self.purchase.id)
        self.assertEqual(record.related_name, self.purchase.name)

        sum_quantity_done = sum(self.purchase.order_line.mapped("move_ids.quantity"))
        self.assertEqual(len(self.purchase.picking_ids), 1)
        self.assertEqual(len(self.purchase.picking_ids[0].move_line_ids), 3)
        self.assertEqual(sum_quantity_done, 19.0)
