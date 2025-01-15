# Copyright 2020 ACSONE
# Copyright 2021 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import datetime

import pytz

from odoo import fields

from odoo.addons.component.core import AbstractComponent


class EDIExchangeInfoOutputMixin(AbstractComponent):
    """Abstract component mixin to generate info for output templates."""

    _name = "edi.info.output.mixin"
    _inherit = "edi.info.provider.mixin"
    # Enable validation of work context attributes
    _work_context_validate_attrs = ["exchange_record"]

    @property
    def record(self):
        return self.work.exchange_record.record

    def generate_info(self):
        """Generate and return data for output info.

        :return: odoo.tools.DotDict
        """
        raise NotImplementedError()

    # helper methods
    @staticmethod
    def _utc_now():
        return datetime.datetime.utcnow().isoformat()

    @staticmethod
    def date_to_string(dt, utc=True):
        if utc:
            dt = dt.astimezone(pytz.UTC)
        return fields.Date.to_string(dt)
