from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestEdiPurchaseDiaparOCA(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.edi_config_diapar = cls.env.ref(
            "edi_purchase_diapar_oca.demo_edi_config_diapar"
        )
        cls.backend = cls.env.ref("edi_purchase_diapar_oca.demo_edi_backend_diapar")
        cls.edi_template_output_diapar = cls.env.ref(
            "edi_purchase_diapar_oca.demo_edi_exchange_template_output_diapar"
        )
        cls.exchange_type_ble = cls.env.ref(
            "edi_purchase_diapar_oca.demo_exchange_diapar_in_despatch_advice"
        )
        cls.exchange_type_ch = cls.env.ref(
            "edi_purchase_diapar_oca.demo_exchange_diapar_in_purchase_price"
        )
        cls.edi_supplier = cls.env.ref("base.res_partner_12")
        cls.edi_supplier.write(
            {
                "is_edi": True,
                "edi_purchase_conf_ids": [Command.set(cls.edi_config_diapar.ids)],
            }
        )
        cls.exchange_type_ble.partner_ids = [Command.set(cls.edi_supplier.ids)]
        cls.exchange_type_ch.partner_ids = [Command.set(cls.edi_supplier.ids)]
        cls.normal_supplier = cls.env.ref("base.res_partner_4")
        cls.product_4 = cls.env.ref("product.product_product_4")
        cls.product_5 = cls.env.ref("product.product_product_5")
        cls.supplier_info_5 = cls.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": cls.product_5.product_tmpl_id.id,
                "partner_id": cls.edi_supplier.id,
                "product_code": "987654",
                "min_qty": 1,
                "price": 10,
            }
        )

    def _create_purchase_order(self, partner, product):
        return self.env["purchase.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_qty": 10,
                            "price_unit": 10,
                        }
                    )
                ],
            }
        )

    def test_purchase_order_confirmation_without_product_code(self):
        order = self._create_purchase_order(self.edi_supplier, self.product_4)
        with self.assertRaises(ValidationError, msg="Please give a supplier code to"):
            order.button_confirm()

    def test_purchase_order_confirmation_with_edi_supplier(self):
        order = self._create_purchase_order(self.edi_supplier, self.product_5)
        order.button_confirm()
        self.assertEqual(order.state, "purchase")
        self.assertEqual(order.exchange_record_count, 1)

    def test_purchase_order_confirmation_with_normal_supplier(self):
        order = self._create_purchase_order(self.normal_supplier, self.product_5)
        order.button_confirm()
        self.assertEqual(order.state, "purchase")
        self.assertEqual(order.exchange_record_count, 0)

    def test_edi_ouput_process_diapar_purchase_order(self):
        order = self._create_purchase_order(self.edi_supplier, self.product_5)
        order.button_confirm()
        exchange_record = order.exchange_record_ids[0]
        exchange_record.backend_id.exchange_generate(exchange_record)
        file_content = exchange_record._get_file_content()
        self.assertTrue(file_content, "The generated file content should not be empty.")
        # Test template output diapar, this shoule be removed?
        constant_file_start = self.edi_template_output_diapar.constant_file_start
        constant_file_end = self.edi_template_output_diapar.constant_file_end
        customer_code = self.edi_template_output_diapar.customer_code
        vrp_code = self.edi_template_output_diapar.vrp_code
        mapping_line_1 = "C" + self.edi_config_diapar.get_datetime_format_ddmmyyyy(
            order.date_planned
        )
        mapping_line_2 = "".join(
            [
                ("D" if vals["origin_code"] == "supplier" else "E")
                + self.edi_config_diapar._fix_lenght(
                    vals["code"], 6, mode="string", replace="0", position="after"
                )
                + self.edi_config_diapar._fix_lenght(
                    vals["quantity"], 3, mode="float", replace="0", position="before"
                )
                for _product, vals in order._consolidate_products().items()
            ]
        )
        self.assertEqual(
            str(file_content).strip(),
            f"{constant_file_start} A{vrp_code}B{customer_code}"
            f"{mapping_line_1}{mapping_line_2}{constant_file_end}",
        )

    def _generate_fake_input_ble_content(self, order, new_quantity):
        """
        Example:
            1AAAAABBBBBCCDDD2026030420260305EEEE
            2AAAAABBBBBCCDDD987654UUUUUUUUUUUUUUUUUUUUUUUUUVVVVV00007-GG
        (where:
            - 1 is the header code, 2 is the lines code
            - 20260305 is the planned date
            - 987654 is the product code
            - 000007 is the new quantity)
        """
        partner_id = order.partner_id.id
        date_planned = order.date_planned.strftime("%Y%m%d")
        header = f"1AAAAABBBBBCCDDD20260304{date_planned}EEEEEE"
        lines = []
        for order_line in order.order_line:
            product = order_line.product_id
            code, _origin_code = product._get_supplier_code_or_ean(partner_id)
            line = (
                f"2AAAAABBBBBCCDDD{code}UUUUUUUUUUUUUUUUUUUUUUUUU"
                + f"VVVVV{str(new_quantity).zfill(5)}-GG"
            )
            lines.append(line)
        return "\n".join([header] + lines)

    def test_edi_input_process_ble(self):
        new_quantity = 7
        order = self._create_purchase_order(self.edi_supplier, self.product_5)
        order.write({"date_planned": "2026-03-05"})
        order.button_confirm()
        exchange_record_out = order.exchange_record_ids[0]
        exchange_record_out.backend_id.exchange_generate(exchange_record_out)

        exchange_record_ble = self.env["edi.exchange.record"].create(
            {
                "backend_id": self.backend.id,
                "type_id": self.exchange_type_ble.id,
                "model": "purchase.order",
                "res_id": order.id,
            }
        )
        self.assertEqual(order.exchange_record_count, 2)

        fake_content = self._generate_fake_input_ble_content(order, new_quantity)
        exchange_record_ble._set_file_content(fake_content)
        exchange_record_ble.write({"edi_exchange_state": "input_received"})
        exchange_record_ble.backend_id.exchange_process(exchange_record_ble)
        self.assertEqual(
            exchange_record_ble.edi_exchange_state,
            "input_processed",
            "The EDI exchange record should be processed successfully.",
        )
        order_picking = order.picking_ids[0]
        picking_update = self.env["picking.update"].search(
            [("name", "=", order_picking.id)]
        )
        self.assertTrue(picking_update, "A picking update record should be created.")
        self.assertTrue(
            picking_update.done, "The picking update should be marked as done."
        )
        moves = order_picking.move_ids
        self.assertEqual(
            len(moves), 1, "There should be one stock move in the picking."
        )
        self.assertEqual(
            moves[0].quantity,
            new_quantity,
            "The stock move quantity should be updated to the new quantity.",
        )

    def _generate_fake_input_ch_content(self):
        product_code = self.supplier_info_5.product_code
        product_name = "BISCOTTE 6CEREALE.300HEUD"
        price_ht = "000015500"
        apply_date = "20060305"
        return (
            f"07{product_code}00015{product_name}{price_ht}"
            + f"0000214100024000033924604808270011013700000030000{apply_date}0001403"
        )

    def test_edi_input_process_ch(self):
        order = self._create_purchase_order(self.edi_supplier, self.product_5)
        order.button_confirm()
        exchange_record_ch = self.env["edi.exchange.record"].create(
            {
                "backend_id": self.backend.id,
                "type_id": self.exchange_type_ch.id,
                "model": "purchase.order",
                "res_id": order.id,
            }
        )
        fake_content = self._generate_fake_input_ch_content().strip()
        exchange_record_ch._set_file_content(fake_content)
        exchange_record_ch.write({"edi_exchange_state": "input_received"})
        exchange_record_ch.backend_id.exchange_process(exchange_record_ch)
        self.assertEqual(
            exchange_record_ch.edi_exchange_state,
            "input_processed",
            "The EDI exchange record should be processed successfully.",
        )

        supplier_price_list = self.env["supplier.price.list"].search(
            [
                ("supplier_id", "=", self.edi_supplier.id),
                ("product_tmpl_id", "=", self.product_5.product_tmpl_id.id),
            ]
        )
        self.assertTrue(
            supplier_price_list, "A supplier price list record should be created."
        )
        self.assertEqual(
            supplier_price_list.price,
            1.55,
            "The price in the supplier price list should be updated to the new price.",
        )
        supllier_info = self.env["product.supplierinfo"].search(
            [
                ("partner_id", "=", self.edi_supplier.id),
                ("product_code", "=", self.supplier_info_5.product_code),
            ]
        )
        self.assertTrue(supllier_info, "The supplier info record should exist.")
        self.assertEqual(
            supllier_info.price,
            1.55,
            "The base price in the supplier info should be updated to the new price.",
        )
