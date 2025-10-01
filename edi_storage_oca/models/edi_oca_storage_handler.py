# # Copyright 2020 ACSONE
# Copyright 2022 Camptocamp
# Copyright 2025 Dixmit
# @author Enric Tobella
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from pathlib import PurePath

from odoo import models

from .. import utils

_logger = logging.getLogger(__name__)


class EdiOcaStorageHandler(models.AbstractModel):
    _name = "edi.oca.storage.handler"
    _inherit = [
        "edi.oca.handler.send",
        "edi.oca.handler.receive",
        "edi.oca.handler.check",
    ]
    _description = "Storage Handler for EDI"

    def send(self, exchange_record):
        result = self.check(exchange_record)
        if not result:
            # all good here
            return True
        filedata = exchange_record.exchange_file
        path = self._get_remote_file_path(exchange_record, "pending")
        utils.add_file(exchange_record.backend_id.storage_id, path.as_posix(), filedata)

    def receive(self, exchange_record):
        return self._get_remote_file(exchange_record, "pending", binary=True)

    def _dir_by_state(self, backend, direction, state):
        """Return remote directory path by direction and state.

        :param direction: string stating direction of the exchange
        :param state: string stating state of the exchange
        :return: PurePath object
        """
        assert direction in ("input", "output")
        assert state in ("pending", "done", "error")
        return PurePath(
            (backend[direction + "_dir_" + state] or "").strip().rstrip("/")
        )

    def _get_remote_file_path(self, exchange_record, state, filename=None):
        """Retrieve remote path for current exchange record."""
        filename = filename or exchange_record.exchange_filename
        direction = exchange_record.direction
        directory = self._dir_by_state(
            exchange_record.backend_id, direction, state
        ).as_posix()
        path = exchange_record.type_id._storage_fullpath(
            directory=directory, filename=filename
        )
        return path

    def _get_remote_file(self, exchange_record, state, filename=None, binary=False):
        """Get file for current exchange_record in the given destination state.

        :param state: string ("pending", "done", "error")
        :param filename: custom file name, exchange_record filename used by default
        :return: remote file content as string
        """
        path = self._get_remote_file_path(exchange_record, state, filename=filename)
        try:
            # TODO: support match via pattern (eg: filename-prefix-*)
            # otherwise is impossible to retrieve input files and acks
            # (the date will never match)
            return utils.get_file(
                exchange_record.backend_id.storage_id, path.as_posix(), binary=binary
            )
        except FileNotFoundError:
            _logger.info(
                "Ignored FileNotFoundError when trying "
                "to get file %s into path %s for state %s",
                filename,
                path,
                state,
            )
            return None
        except OSError:
            _logger.info(
                "Ignored OSError when trying to get file %s into path %s for state %s",
                filename,
                path,
                state,
            )
            return None

    def check(self, exchange_record):
        return self._exchange_output_check(exchange_record)

    def _exchange_output_check(self, exchange_record):
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
