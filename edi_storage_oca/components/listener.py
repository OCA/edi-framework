# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import functools
import os
from pathlib import PurePath

from odoo.addons.component.core import Component


class EdiStorageListener(Component):
    _name = "edi.storage.component.listener"
    _inherit = "base.event.listener"

    def _move_file(self, storage, from_dir_str, to_dir_str, filename):
        from_dir = PurePath(from_dir_str)
        to_dir = PurePath(to_dir_str)
        # - storage.list_files now includes path in fs_storage, breaking change
        # - we remove path
        # TODO: clean this up, .list_files is deprecated in fs_storage
        files = storage.list_files(from_dir.as_posix())
        files = [os.path.basename(f) for f in files]
        if filename not in files:
            return False
        # TODO: clean this up, .move_files is deprecated in fs_storage
        self._add_post_commit_hook(
            storage.move_files, [(from_dir / filename).as_posix()], to_dir.as_posix()
        )
        return True

    def _add_post_commit_hook(self, move_func, sftp_filepath, sftp_destination_path):
        """Add hook after commit to move the file when transaction is over."""
        self.env.cr.postcommit.add(
            functools.partial(move_func, sftp_filepath, sftp_destination_path)
        )

    def on_edi_exchange_done(self, record):
        storage = record.backend_id.storage_id
        res = False
        if record.direction == "input" and storage:
            file = record.exchange_filename
            pending_dir = record.type_id._storage_fullpath(
                record.backend_id.input_dir_pending
            ).as_posix()
            done_dir = record.type_id._storage_fullpath(
                record.backend_id.input_dir_done
            ).as_posix()
            error_dir = record.type_id._storage_fullpath(
                record.backend_id.input_dir_error
            ).as_posix()
            if not done_dir:
                return res
            res = self._move_file(storage, pending_dir, done_dir, file)
            if not res:
                # If a file previously failed it should have been previously
                # moved to the error dir, therefore it is not present in the
                # pending dir and we need to retry from error dir.
                res = self._move_file(storage, error_dir, done_dir, file)
        return res

    def on_edi_exchange_error(self, record):
        storage = record.backend_id.storage_id
        res = False
        if record.direction == "input" and storage:
            file = record.exchange_filename
            pending_dir = record.type_id._storage_fullpath(
                record.backend_id.input_dir_pending
            ).as_posix()
            error_dir = record.type_id._storage_fullpath(
                record.backend_id.input_dir_error
            ).as_posix()
            if error_dir:
                res = self._move_file(storage, pending_dir, error_dir, file)
        return res
