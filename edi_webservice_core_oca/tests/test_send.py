# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from urllib.parse import urlparse

import responses
from requests import PreparedRequest, Session

from .common import TestEDIWebserviceCoreBase


class TestSend(TestEDIWebserviceCoreBase):
    @classmethod
    def setUpClass(cls):
        cls._super_send = Session.send
        super().setUpClass()

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
        kwargs = handler._get_call_params(self.record, ws_settings)
        self.assertEqual(kwargs["data"], "This is a simple file")

    def test_call_params_extra_kwargs_from_settings(self):
        settings = """
        execution_model:
          send:
            webservice:
              kwargs:
                headers:
                  X-Demo: demo-value
        """
        self.record.type_id.set_settings(settings)
        handler = self._get_handler()
        ws_settings = handler._get_ws_settings(self.record)
        kwargs = handler._get_call_params(self.record, ws_settings)
        self.assertEqual(kwargs["headers"], {"X-Demo": "demo-value"})

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
        self.record.type_id.webservice_send_as_bytes = True
        handler = self._get_handler()
        ws_settings = handler._get_ws_settings(self.record)
        kwargs = handler._get_call_params(self.record, ws_settings)
        self.assertEqual(kwargs["data"], b"This is a simple file")

    @responses.activate
    def test_exchange_send_dispatch(self):
        # `send_model_id` + `webservice_endpoint_id` on the exchange type
        # are enough for the regular EDI framework dispatch
        # (`backend.exchange_send`) to reach our handler - not just direct
        # calls to it.
        self.record.edi_exchange_state = "output_pending"
        url = "https://foo.test/push/here"
        responses.add(responses.POST, url, body="{}")
        self.backend.exchange_send(self.record)
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(responses.calls[0].request.body, "This is a simple file")
