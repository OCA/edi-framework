# Copyright 2020 ACSONE
# Copyright 2022 Camptocamp
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging
from pathlib import PurePath

from .. import utils

_logger = logging.getLogger(__file__)


class EDIStorageMixin:
    def _get_dir_by_state(self, backend, direction, state):
        """Return remote directory path by direction and state.

        :param backend: edi.backend recordset
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
        directory = self._get_dir_by_state(
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
