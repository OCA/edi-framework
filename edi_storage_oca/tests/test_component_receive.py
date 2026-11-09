# Copyright 2026 Ametras intelligence GmbH
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from unittest import mock

from odoo.exceptions import UserError

from odoo.addons.edi_storage_oca.components import base as storage_base

from .common import FS_STORAGE_MOCK_PATH, TestEDIStorageBase


class EDIStorageReceiveTestCase(TestEDIStorageBase):
    @classmethod
    def _setup_records(cls):
        res = super()._setup_records()
        cls.record_pending = cls.backend.create_record(
            "test_csv_input",
            {
                "model": cls.partner._name,
                "res_id": cls.partner.id,
                "exchange_filename": "test-input-receive.csv",
                "edi_exchange_state": "input_pending",
            },
        )
        cls.receiver = cls.backend._find_component(
            cls.partner._name,
            ["storage.receive"],
            work_ctx={"exchange_record": cls.record_pending},
        )
        return res

    def _mock_get_file(self, side_effect):
        return mock.patch(FS_STORAGE_MOCK_PATH + ".get_file", side_effect=side_effect)

    def test_receive_returns_the_file_content(self):
        with self._mock_get_file([b"file content"]):
            self.assertEqual(self.receiver.receive(), b"file content")

    def test_receive_raises_on_missing_file(self):
        with self._mock_get_file(FileNotFoundError("Simulated missing file")):
            with self.assertRaisesRegex(FileNotFoundError, "Simulated missing file"):
                self.receiver.receive()

    def test_receive_raises_on_storage_error(self):
        with self._mock_get_file(OSError("Simulated dead SFTP connection")):
            with self.assertLogs(storage_base._logger, level="WARNING") as logs:
                with self.assertRaisesRegex(
                    UserError, "Storage error while reading .*dead SFTP connection"
                ):
                    self.receiver.receive()
        self.assertIn("Simulated dead SFTP connection", logs.output[0])

    def test_storage_error_puts_the_record_in_receive_error(self):
        with self._mock_get_file(OSError("Simulated dead SFTP connection")):
            with self.assertLogs(storage_base._logger, level="WARNING"):
                self.backend.with_context(
                    _edi_receive_break_on_error=False
                ).exchange_receive(self.record_pending)
        self.env.flush_all()
        self.env.invalidate_all()
        self.assertEqual(
            self.record_pending.edi_exchange_state,
            "input_receive_error",
            msg="A failed read must not leave the record received without content",
        )
        self.assertIn("dead SFTP connection", self.record_pending.exchange_error)
        self.assertFalse(
            self.record_pending.exchange_file,
            msg="A failed read must not store any content on the record",
        )

    def test_other_reads_still_ignore_storage_errors(self):
        with self._mock_get_file(OSError("Simulated dead SFTP connection")):
            with self.assertLogs(storage_base._logger, level="WARNING"):
                self.assertIsNone(self.checker._get_remote_file("pending"))
        with self._mock_get_file(FileNotFoundError("Simulated missing file")):
            self.assertIsNone(self.checker._get_remote_file("pending"))
