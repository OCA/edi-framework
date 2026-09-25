# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from urllib.parse import urlparse

import responses
from requests import PreparedRequest, Session

from odoo import exceptions

from .common import TestEDIWebserviceCoreBase


class TestSend(TestEDIWebserviceCoreBase):
    @classmethod
    def setUpClass(cls):
        cls._super_send = Session.send
        super().setUpClass()

    @classmethod
    def _setup_records(cls):
        result = super()._setup_records()
        cls.ws_backend = cls.backend.webservice_backend_id
        cls.settings = """
        execution_model:
          send:
            webservice:
              method: post
              kwargs:
                url_params:
                  endpoint: push/here
        """
        cls.record.type_id.set_settings(cls.settings)
        return result

    @classmethod
    def _request_handler(cls, s: Session, r: PreparedRequest, /, **kw):
        # Allow request to test custom URL
        if urlparse(r.url).netloc == "foo.test":
            return cls._super_send(s, r)
        return super()._request_handler(s, r, **kw)

    def _get_handler(self):
        return self.env["edi.webservice.send"]

    def test_call_params(self):
        handler = self._get_handler()
        ws_settings = handler._get_ws_settings(self.record)
        method, pargs, kwargs = handler._get_call_params(self.record, ws_settings)
        self.assertEqual(method, "post")
        self.assertEqual(pargs, [])
        self.assertEqual(kwargs["data"], "This is a simple file")
        self.assertEqual(kwargs["url_params"], {"endpoint": "push/here"})

    def test_no_method(self):
        handler = self._get_handler()
        msg = "`method` is required in `webservice` type settings"
        with self.assertRaisesRegex(exceptions.UserError, msg):
            handler._get_call_params(self.record, {})

    @responses.activate
    def test_send(self):
        url = "https://foo.test/push/here"
        responses.add(responses.POST, url, body="{}")
        result = self._get_handler().send(self.record)
        self.assertEqual(result, b"{}")
        self.assertEqual(
            responses.calls[0].request.headers["Content-Type"], "application/xml"
        )
        self.assertEqual(responses.calls[0].request.body, "This is a simple file")

    def test_send_as_bytes(self):
        settings = """
        execution_model:
          send:
            webservice:
              method: post
              send_as_bytes: true
              kwargs:
                url_params:
                  endpoint: push/here
        """
        self.record.type_id.set_settings(settings)
        handler = self._get_handler()
        ws_settings = handler._get_ws_settings(self.record)
        method, pargs, kwargs = handler._get_call_params(self.record, ws_settings)
        self.assertEqual(kwargs["data"], b"This is a simple file")

    @responses.activate
    def test_exchange_send_dispatch(self):
        # `send_model_id` on the exchange type is enough for the regular
        # EDI framework dispatch (`backend.exchange_send`) to reach our
        # handler - not just direct calls to it.
        self.record.type_id.send_model_id = self.env.ref(
            "edi_webservice_core_oca.model_edi_webservice_send"
        )
        self.record.edi_exchange_state = "output_pending"
        url = "https://foo.test/push/here"
        responses.add(responses.POST, url, body="{}")
        self.backend.exchange_send(self.record)
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(responses.calls[0].request.body, "This is a simple file")
