# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from requests import Response

from odoo import models


class EDIWebserviceSend(models.AbstractModel):
    """Generic handler for sending EDI exchange files through a webservice.

    The exchange type's ``webservice_endpoint_id`` is used to perform the
    call - its own HTTP method applies. Extra call parameters (headers,
    query params, ...) can be provided via the exchange type's advanced
    settings, under ``execution_model.send.webservice``.

    """

    _name = "edi.webservice.send"
    _inherit = "edi.oca.handler.send"
    _description = "EDI WebService Send Handler"

    def send(self, exchange_record):
        endpoint = exchange_record.type_id.webservice_endpoint_id
        ws_settings = self._get_ws_settings(exchange_record)
        kwargs = self._get_call_params(exchange_record, ws_settings)
        response = endpoint.call(**kwargs)
        if not isinstance(response, Response):
            # backward compat for obsolete `content_only` param
            return response
        return response.content

    def _get_ws_settings(self, exchange_record):
        settings = exchange_record.type_id.get_settings()
        return settings.get("execution_model", {}).get("send", {}).get("webservice", {})

    def _get_call_params(self, exchange_record, ws_settings):
        kwargs = ws_settings.get("kwargs", {})
        kwargs["data"] = self._get_data(exchange_record)
        return kwargs

    def _get_data(self, exchange_record):
        # By sending as bytes `requests` won't try to guess and/or alter the encoding.
        as_bytes = exchange_record.type_id.webservice_send_as_bytes
        return exchange_record._get_file_content(as_bytes=as_bytes)
