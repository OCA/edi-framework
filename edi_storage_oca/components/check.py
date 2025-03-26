# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo.addons.component.core import Component
from odoo.addons.edi_storage_core_oca.abstracts.check import EDIStorageCheckMixin

_logger = logging.getLogger(__name__)


class EDIStorageCheckComponentMixin(EDIStorageCheckMixin, Component):
    _name = "edi.storage.component.check"
    _inherit = [
        "edi.component.check.mixin",
        "edi.storage.component.mixin",
    ]
    _usage = "storage.check"

    def check(self):
        return self._exchange_output_check()

    def _exchange_output_check(self):
        """Check status output exchange and update record.

        1. check if the file has been processed already (done)
        2. if yes, post message and exit
        3. if not, check for errors
        4. if no errors, return

        :return: boolean
            * False if there's nothing else to be done
            * True if file still need action
        """
        return self._exchange_output_check_abstract(self.exchange_record)
