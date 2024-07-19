# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.edi_oca.tests.common import EDIBackendTestMixin
from odoo.addons.edi_sale_oca.tests.common import OrderMixin


class TestSaleOrder(BaseCommon, OrderMixin, EDIBackendTestMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_records()
        cls.exchange_type_in.exchange_filename_pattern = "{record.id}-{type.code}-{dt}"
        cls.exc_record_in = cls.backend.create_record(
            cls.exchange_type_in.code, {"edi_exchange_state": "input_received"}
        )
        cls._setup_order(
            origin_exchange_record_id=cls.exc_record_in.id,
        )

    def test_source_edi(self):
        order = self.sale
        self.assertEqual(
            order.edi_source_id,
            self.env.ref("edi_utm_oca.utm_source_edi"),
        )
