# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging

_logger = logging.getLogger(__name__)


class EDIStorageCheckMixin:
    def _exchange_output_check_abstract(self, exchange_record):
        """Check status output exchange and update record.

        1. check if the file has been processed already (done)
        2. if yes, post message and exit
        3. if not, check for errors
        4. if no errors, return

        :return: boolean
            * False if there's nothing else to be done
            * True if file still need action
        """
        if self._get_remote_file(exchange_record, "done"):
            _logger.info(
                "%s done",
                exchange_record.identifier,
            )
            if not exchange_record.edi_exchange_state == "output_sent_and_processed":
                exchange_record.edi_exchange_state = "output_sent_and_processed"
                exchange_record._notify_done()
            return False

        error = self._get_remote_file(exchange_record, "error")
        if error:
            _logger.info(
                "%s error",
                exchange_record.identifier,
            )
            # Assume a text file will be placed there w/ the same name and error suffix
            err_filename = exchange_record.exchange_filename + ".error"
            error_report = (
                self._get_remote_file(exchange_record, "error", filename=err_filename)
                or "no-report"
            )
            if exchange_record.edi_exchange_state == "output_sent":
                exchange_record.update(
                    {
                        "edi_exchange_state": "output_sent_and_error",
                        "exchange_error": error_report,
                    }
                )
                exchange_record._notify_error("process_ko")
            return False
        return True
