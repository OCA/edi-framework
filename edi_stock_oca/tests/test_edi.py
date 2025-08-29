# Copyright 2022 Creu Blanca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from unittest import mock

from odoo.addons.edi_oca.tests.common import EDIBackendCommonComponentTestCase


class TestProcessComponent(EDIBackendCommonComponentTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend = cls.env.ref("edi_stock_oca.demo_edi_backend")
        cls.exc_type_out = cls.env.ref("edi_stock_oca.demo_edi_exc_type_order_out")
        cls.edi_conf = cls.env.ref("edi_stock_oca.demo_edi_configuration_done")
        cls.partner.edi_stock_picking_conf_ids = cls.edi_conf
        cls.warehouse = cls.env["stock.warehouse"].search([], limit=1)
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.picking_type = cls.env["stock.picking.type"].create(
            {
                "name": "Test Picking Type",
                "sequence_code": "TPT",
                "code": "internal",
                "default_location_src_id": cls.supplier_location.id,
                "default_location_dest_id": cls.stock_location.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "default_code": "1234567",
            }
        )

    def _create_picking(self):
        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.picking_type.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        move_a = self.env["stock.move"].create(
            {
                "name": self.product.name,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "product_uom": self.product.uom_id.id,
                "picking_id": picking.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        move_a.move_line_ids.quantity = 4
        return picking

    def _mock_generate(self, exc_rec):
        return f"TRANSFER STATE {exc_rec.record.state}"

    @mock.patch("odoo.addons.edi_core_oca.models.edi_backend.EDIBackend._validate_data")
    @mock.patch(
        "odoo.addons.edi_core_oca.models.edi_backend.EDIBackend._exchange_generate"
    )
    @mock.patch("odoo.addons.edi_core_oca.models.edi_backend.EDIBackend._exchange_send")
    def test_picking_cancel_flow(self, mock_send, mock_generate, mock_validate):
        mock_generate.side_effect = self._mock_generate
        picking = self._create_picking()
        self.assertFalse(picking.exchange_record_ids)
        picking.action_confirm()
        self.assertEqual(len(picking.exchange_record_ids), 1)
        record1 = picking.exchange_record_ids
        self.assertEqual(record1.type_id, self.exc_type_out)
        self.assertEqual(record1._get_file_content(), "TRANSFER STATE assigned")
        picking.action_cancel()
        self.assertEqual(len(picking.exchange_record_ids), 2)
        record2 = picking.exchange_record_ids - record1
        self.assertEqual(record2.type_id, self.exc_type_out)
        self.assertEqual(record2._get_file_content(), "TRANSFER STATE cancel")

    @mock.patch("odoo.addons.edi_core_oca.models.edi_backend.EDIBackend._validate_data")
    @mock.patch(
        "odoo.addons.edi_core_oca.models.edi_backend.EDIBackend._exchange_generate"
    )
    @mock.patch("odoo.addons.edi_core_oca.models.edi_backend.EDIBackend._exchange_send")
    def test_picking_done_flow(self, mock_send, mock_generate, mock_validate):
        mock_generate.side_effect = self._mock_generate
        picking = self._create_picking()
        self.assertFalse(picking.exchange_record_ids)
        picking.action_confirm()
        self.assertEqual(len(picking.exchange_record_ids), 1)
        record1 = picking.exchange_record_ids
        self.assertEqual(record1.type_id, self.exc_type_out)
        self.assertEqual(record1._get_file_content(), "TRANSFER STATE assigned")
        picking.button_validate()
        self.assertEqual(len(picking.exchange_record_ids), 2)
        record2 = picking.exchange_record_ids - record1
        self.assertEqual(record2.type_id, self.exc_type_out)
        self.assertEqual(record2._get_file_content(), "TRANSFER STATE done")
