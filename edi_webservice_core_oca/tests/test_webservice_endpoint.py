# Copyright 2026 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from .common import TestEDIWebserviceCoreBase


class TestWebserviceEndpoint(TestEDIWebserviceCoreBase):
    def test_exchange_type_count(self):
        """Count reflects exchange types linked to the endpoint."""
        self.assertEqual(self.endpoint.exchange_type_count, 1)
        self.record.type_id.webservice_endpoint_id = False
        self.assertEqual(self.endpoint.exchange_type_count, 0)

    def test_action_view_exchange_types(self):
        """Action opens exchange types filtered on this endpoint."""
        action = self.endpoint.action_view_exchange_types()
        self.assertEqual(action["res_model"], "edi.exchange.type")
        self.assertEqual(
            action["domain"], [("webservice_endpoint_id", "=", self.endpoint.id)]
        )
