# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.edi_core_oca.tests.common import EDIBackendCommonTestCase


class TestEdiWebserviceCore(EDIBackendCommonTestCase):
    def test_webservice_backend_id(self):
        webservice = self.env["webservice.backend"].create(
            {
                "name": "WebService",
                "protocol": "http",
                "url": "https://localhost.demo.odoo/",
                "tech_name": "demo_ws_core",
                "auth_type": "none",
            }
        )
        self.backend.webservice_backend_id = webservice
        self.assertEqual(self.backend.webservice_backend_id, webservice)
