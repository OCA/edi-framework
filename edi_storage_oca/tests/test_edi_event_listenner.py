# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64
from unittest import mock

from odoo.tests.common import TransactionCase

RECORD_MOCK_PATH = (
    "odoo.addons.edi_storage_oca.models.edi_exchange_record.EDIExchangeRecord"
)
BACKEND_MOCK_PATH = (
    "odoo.addons.edi_core_oca.models.edi_backend.EDIBackend._get_exec_handler"
)


class EDIBackendTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend = cls.env.ref("edi_storage_oca.demo_edi_backend_storage")
        cls.exchange_type = cls.env.ref(
            "edi_storage_oca.demo_edi_type_csv_input", raise_if_not_found=False
        )
        if not cls.exchange_type:
            cls.exchange_type = cls.env["edi.exchange.type"].create(
                {
                    "name": "Test CSV Input",
                    "code": "test_csv_input",
                    "direction": "input",
                    "backend_id": cls.backend.id,
                    "backend_type_id": cls.backend.backend_type_id.id,
                }
            )
        cls.record = cls.env["edi.exchange.record"].create(
            {
                "type_id": cls.exchange_type.id,
                "backend_id": cls.backend.id,
                "exchange_file": base64.b64encode(b"1234"),
            }
        )

    def setUp(self):
        super().setUp()
        self.fake_move_args = None

    def _mock_listener_move_file(self):
        def _move_file_mocked(record, storage, from_dir_str, to_dir_str, filename):
            if not self.fake_move_args:
                self.fake_move_args = [storage, from_dir_str, to_dir_str, filename]
            return True

        return mock.patch(
            RECORD_MOCK_PATH + "._move_file",
            autospec=True,
            side_effect=_move_file_mocked,
        )

    def _mock_process_handler(self):
        def _fake_exec_handler(backend, record, step):
            def handler(rec):
                if rec.env.context.get("test_break_process"):
                    rec.write({"edi_exchange_state": "input_processed_error"})
                    rec._notify_error("process_ko")
                    return False
                rec.write({"edi_exchange_state": "input_processed"})
                rec._notify_done()
                return True

            return handler

        return mock.patch(
            BACKEND_MOCK_PATH, autospec=True, side_effect=_fake_exec_handler
        )

    def test_01_process_record_success(self):
        with self._mock_listener_move_file(), self._mock_process_handler():
            self.record.write(
                {
                    "edi_exchange_state": "input_received",
                    "storage_id": self.backend.storage_id.id,
                }
            )
            self.record._set_file_content("TEST %d" % self.record.id)
            self.record.action_exchange_process()

            storage, from_dir_str, to_dir_str, filename = self.fake_move_args
            self.assertEqual(storage, self.backend.storage_id)
            self.assertEqual(from_dir_str, self.backend.input_dir_pending)
            self.assertEqual(to_dir_str, self.backend.input_dir_done)
            self.assertEqual(filename, self.record.exchange_filename)

    def test_02_process_record_with_error(self):
        with self._mock_listener_move_file(), self._mock_process_handler():
            self.record.write(
                {
                    "edi_exchange_state": "input_received",
                    "storage_id": self.backend.storage_id.id,
                }
            )
            self.record._set_file_content("TEST %d" % self.record.id)
            self.record.with_context(
                test_break_process="OOPS!"
            ).action_exchange_process()

            storage, from_dir_str, to_dir_str, filename = self.fake_move_args
            self.assertEqual(storage, self.backend.storage_id)
            self.assertEqual(from_dir_str, self.backend.input_dir_pending)
            self.assertEqual(to_dir_str, self.backend.input_dir_error)
            self.assertEqual(filename, self.record.exchange_filename)
