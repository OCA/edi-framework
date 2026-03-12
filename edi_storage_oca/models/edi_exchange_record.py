# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import functools
import os
from pathlib import PurePath

from odoo import fields, models

from .. import utils


class EDIExchangeRecord(models.Model):
    _inherit = "edi.exchange.record"

    storage_id = fields.Many2one(
        comodel_name="fs.storage",
        readonly=True,
        string="FS Storage",
        help="Record created from a file found in this FS storage",
    )

    def _move_file(self, storage, from_dir_str, to_dir_str, filename):
        from_dir = PurePath(from_dir_str)
        to_dir = PurePath(to_dir_str)
        # - storage.list_files now includes path in fs_storage, breaking change
        # - we remove path
        files = utils.list_files(storage, from_dir.as_posix())
        files = [os.path.basename(f) for f in files]
        if filename not in files:
            return False
        self._add_post_commit_hook(
            utils.move_files,
            storage,
            [(from_dir / filename).as_posix()],
            to_dir.as_posix(),
        )
        return True

    def _add_post_commit_hook(
        self, move_func, storage, sftp_filepath, sftp_destination_path
    ):
        """Add hook after commit to move the file when transaction is over."""
        self.env.cr.postcommit.add(
            functools.partial(move_func, storage, sftp_filepath, sftp_destination_path)
        )

    def on_edi_exchange_done(self):
        storage = self.storage_id
        res = False
        if self.direction == "input" and storage:
            file = self.exchange_filename
            pending_dir = self.type_id._storage_fullpath(
                self.backend_id.input_dir_pending
            ).as_posix()
            done_dir = self.type_id._storage_fullpath(
                self.backend_id.input_dir_done
            ).as_posix()
            error_dir = self.type_id._storage_fullpath(
                self.backend_id.input_dir_error
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

    def on_edi_exchange_error(self):
        storage = self.storage_id
        res = False
        if self.direction == "input" and storage:
            file = self.exchange_filename
            pending_dir = self.type_id._storage_fullpath(
                self.backend_id.input_dir_pending
            ).as_posix()
            error_dir = self.type_id._storage_fullpath(
                self.backend_id.input_dir_error
            ).as_posix()
            if error_dir:
                res = self._move_file(storage, pending_dir, error_dir, file)
        return res
