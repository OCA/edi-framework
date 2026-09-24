# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from requests import Response

from odoo import _, exceptions, models


class EDIWebserviceSend(models.AbstractModel):
    """Generic handler for sending EDI exchange files through a webservice.

    Configuration is expected to come from the exchange type's advanced
    settings, under ``execution_model.send.webservice``.
    """

    _name = "edi.webservice.send"
    _inherit = "edi.oca.handler.send"
    _description = "EDI WebService Send Handler"

    def send(self, exchange_record):
        ws_settings = self._get_ws_settings(exchange_record)
        method, pargs, kwargs = self._get_call_params(exchange_record, ws_settings)
        response = exchange_record.backend_id.webservice_backend_id.call(
            method, *pargs, **kwargs
        )
        if not isinstance(response, Response):
            # backward compat for obsolete `content_only` param
            return response
        return response.content

    def _get_ws_settings(self, exchange_record):
        settings = exchange_record.type_id.get_settings()
        return settings.get("execution_model", {}).get("send", {}).get("webservice", {})

    def _get_call_params(self, exchange_record, ws_settings):
        try:
            method = ws_settings["method"].lower()
        except KeyError as err:
            raise exceptions.UserError(
                _("`method` is required in `webservice` type settings.")
            ) from err
        pargs = ws_settings.get("pargs", [])
        kwargs = ws_settings.get("kwargs", {})
        kwargs["data"] = self._get_data(exchange_record, ws_settings)
        return method, pargs, kwargs

    def _get_data(self, exchange_record, ws_settings):
        # By sending as bytes `requests` won't try to guess and/or alter the encoding.
        as_bytes = ws_settings.get("send_as_bytes")
        return exchange_record._get_file_content(as_bytes=as_bytes)
