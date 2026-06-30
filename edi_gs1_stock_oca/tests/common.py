# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from uuid import uuid4

from odoo import fields
from odoo.tests import Form

from odoo.addons.edi_gs1_oca.tests.common import BaseTestCase


class DeliveryMixin:
    @classmethod
    def _create_purchase_order(cls, values, view=None):
        """Create a purchase order

        :return: purchase order
        """
        po = Form(cls.env["purchase.order"], view=view)
        po.partner_ref = str(uuid4())[:6]
        po.date_planned = fields.Date.today()
        for k, v in values.items():
            setattr(po, k, v)
        return po.save()

    @classmethod
    def _create_purchase_order_line(cls, purchase_order, view=None, **kw):
        """
        Create a purchase order line for give order
        :return: line
        """
        values = {}
        values.update(kw)
        po = Form(purchase_order, view=view)
        with po.order_line.new() as po_line:
            for k, v in values.items():
                setattr(po_line, k, v)
        return po.save()


class ShipmentTestCaseBase(BaseTestCase, DeliveryMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

    @classmethod
    def _create_product(cls, name, barcode):
        return cls.env["product.product"].create(
            {
                "name": name,
                "is_storable": True,
                "type": "consu",
                "barcode": barcode,
                "weight": 1.0,
            }
        )

    @classmethod
    def _setup_order(cls):
        cls.product_a = cls._create_product("GS1 Product A", "1" * 14)
        cls.product_b = cls._create_product("GS1 Product B", "2" * 14)
        cls.product_c = cls._create_product("GS1 Product C", "3" * 14)
        cls.vendor = cls.env["res.partner"].create({"name": "GS1 Vendor"})
        cls.purchase = cls._create_purchase_order(
            {
                "partner_id": cls.vendor,
                "date_planned": "2020-07-12",
            }
        )
        lines = [
            {"product_id": cls.product_a, "product_qty": 300},
            {"product_id": cls.product_b, "product_qty": 200},
            {"product_id": cls.product_c, "product_qty": 100},
        ]
        for line in lines:
            cls._create_purchase_order_line(cls.purchase, **line)

        cls.purchase.button_approve()
        cls.delivery = cls.purchase.picking_ids[0]
        cls.delivery.scheduled_date = "2020-07-12 12:00:00"
        cls.carrier = cls.env["res.partner"].create(
            {
                "name": "GS1 Carrier",
                "gln_code": "123".zfill(13),
                "ref": "CARRIER#1",
            }
        )
