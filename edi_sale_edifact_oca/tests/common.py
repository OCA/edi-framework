# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.sale_order_import_edifact.tests.common import get_test_data


class OrderInboundTestMixin:
    @classmethod
    def _setup_inbound_order(cls, backend):
        cls.exc_type_in = cls.env.ref(
            "edi_sale_edifact_oca.demo_edi_exc_type_edifact_order_in"
        )
        cls.exc_type_in.backend_id = backend
        cls.exc_record_in = backend.create_record(
            cls.exc_type_in.code, {"edi_exchange_state": "input_received"}
        )
        cls.edifact_data = get_test_data(cls.env)
        fname = "Retail_EDIFACT_ORDERS_sample1.txt"
        cls.order_data = cls.edifact_data[fname]
        fcontent = cls.order_data._get_content()
        cls.exc_record_in._set_file_content(fcontent)
        cls.err_msg_already_imported = "Sales order has already been imported before"
