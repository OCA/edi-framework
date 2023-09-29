# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo.tools import pycompat

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class EDIStorageCheckComponentMixin(Component):

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
        if self._get_remote_file("done"):
            _logger.info(
                "%s done",
                self.exchange_record.identifier,
            )
            if (
                not self.exchange_record.edi_exchange_state
                == "output_sent_and_processed"
            ):
                self.exchange_record.edi_exchange_state = "output_sent_and_processed"
                self.exchange_record._notify_done()
            return False

        error = self._get_remote_file("error")
        if error:
            _logger.info(
                "%s error",
                self.exchange_record.identifier,
            )
            # Assume a text file will be placed there w/ the same name and error suffix
            err_filename = self.exchange_record.exchange_filename + ".error"
            error_report = (
                self._get_remote_file("error", filename=err_filename) or "no-report"
            )
            if self.exchange_record.edi_exchange_state == "output_sent":
                self.exchange_record.update(
                    {
                        "edi_exchange_state": "output_sent_and_error",
                        "exchange_error": pycompat.to_text(error_report),
                    }
                )
                self.exchange_record._notify_error("process_ko")
            return False
        return True
