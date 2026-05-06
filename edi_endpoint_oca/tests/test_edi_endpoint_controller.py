# Copyright 2021 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64
import json
import os
import unittest

from odoo.tests import HttpCase, RecordCapturer


@unittest.skipIf(os.getenv("SKIP_HTTP_CASE"), "EDIEndpointHttpCase skipped")
class EDIEndpointHttpCase(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # force sync for demo records
        cls.env["edi.endpoint"].search([])._handle_registry_sync()

    def test_call1(self):
        endpoint = "/edi/demo/try"
        response = self.url_open(endpoint)
        self.assertEqual(response.status_code, 401)
        # Let's login now
        self.authenticate("admin", "admin")
        response = self.url_open(endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Created record:", response.content.decode())

    def test_handle_exec_create_exchange_record(self):
        self.authenticate("admin", "admin")
        body = json.dumps({"hello": "world"}).encode()
        with RecordCapturer(self.env["edi.exchange.record"], []) as capture:
            response = self.url_open(
                "/edi/demo/create",
                headers={"Content-Type": "application/json"},
                data=body,
                timeout=10,
            )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "queued")
        self.assertEqual(len(capture.records), 1)
        record = capture.records
        self.assertEqual(record.identifier, payload["id"])
        self.assertEqual(record.edi_exchange_state, "new")
        self.assertEqual(base64.b64decode(record.exchange_file), body)
