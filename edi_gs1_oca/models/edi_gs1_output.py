# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

import pytz

from odoo import fields, models
from odoo.tools import DotDict

from ..utils import xml_purge_nswrapper


class EdiGs1OutputMixin(models.AbstractModel):
    """Common GS1 output generation mixin.

    Replaces the old ``edi.output.info.mixin`` (info provider) and the
    ``edi.exchange.template.output`` QWeb rendering, both dropped in the
    new EDI OCA architecture. Concrete generators inherit this mixin
    together with ``edi.oca.handler.generate``.
    """

    _name = "edi.gs1.output.mixin"
    _description = "GS1 EDI output mixin"

    # --- info provider (ported from edi.info.provider.mixin) ---
    def generate_info(self, exchange_record, **kw):
        """Generate and return data for output info.

        :return: odoo.tools.DotDict
        """
        return DotDict(self._generate_info(exchange_record, **kw))

    def _generate_info(self, exchange_record, **kw):
        raise NotImplementedError("You must provide `_generate_info`")

    @staticmethod
    def _utc_now():
        return datetime.datetime.utcnow().isoformat()

    @staticmethod
    def date_to_string(dt, utc=True):
        if utc:
            dt = dt.astimezone(pytz.UTC)
        return fields.Date.to_string(dt)

    def _document_action_code(self, replace_existing=False):
        # Brand new file -> "ADD", otherwise replacing an existing one
        return "CHANGE_BY_REFRESH" if replace_existing else "ADD"

    # --- template rendering (ported from edi.exchange.template.output) ---
    def _get_render_values(self, exchange_record, **kw):
        """Collect values to render a GS1 QWeb template."""
        values = {
            "exchange_record": exchange_record,
            "record": exchange_record.record,
            "backend": exchange_record.backend_id,
            # Default identifier to the exchange record one
            "instance_identifier": exchange_record.identifier,
            "doc_type": None,
            "utc_now": self._utc_now,
            "date_to_string": self.date_to_string,
            "render_edi_template": self._render_edi_template,
            "info": {},
        }
        values.update(kw)
        return values

    def _render_edi_template(self, exchange_record, xmlid, **kw):
        """Render a GS1 QWeb template and purge the `nswrapper` helpers.
        TODO: check if edi_exchange_template_oca could replace this rendering part"""
        values = self._get_render_values(exchange_record, **kw)
        output = self.env["ir.qweb"]._render(xmlid, values)
        return xml_purge_nswrapper(output)
