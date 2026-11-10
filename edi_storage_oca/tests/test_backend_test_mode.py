# Copyright 2026 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html>).

from .common import TestEDIStorageBase


class TestBackendTestMode(TestEDIStorageBase):
    def test_test_mode_uses_test_directories(self):
        """In test mode the backend resolves test_* dirs, else live."""
        self.backend.test_input_dir_pending = "/test_in/pending/"
        self.backend.test_output_dir_pending = "/test_out/pending/"
        self.backend.test_mode = True
        self.assertEqual(
            self.backend.get_conn_parameter("input_dir_pending"),
            "/test_in/pending/",
        )
        self.assertEqual(
            self.backend.get_conn_parameter("output_dir_pending"),
            "/test_out/pending/",
        )
        # An empty test dir falls back to the live value.
        self.assertEqual(
            self.backend.get_conn_parameter("input_dir_done"),
            self.backend.input_dir_done,
        )
        self.backend.test_mode = False
        self.assertEqual(
            self.backend.get_conn_parameter("input_dir_pending"),
            self.backend.input_dir_pending,
        )

    def test_test_mode_uses_test_storage(self):
        """Test mode can point at a different FS storage entirely."""
        test_storage = self.env["fs.storage"].create(
            {
                "name": "Test FS Storage",
                "protocol": "odoofs",
                "code": "odoofs_test",
            }
        )
        self.backend.test_storage_id = test_storage
        self.backend.test_mode = True
        self.assertEqual(self.backend.get_conn_parameter("storage_id"), test_storage)
        self.backend.test_mode = False
        self.assertEqual(
            self.backend.get_conn_parameter("storage_id"), self.backend.storage_id
        )

    def test_other_parameters_unaffected(self):
        """Params outside the whitelist always resolve to live values."""
        self.backend.test_mode = True
        self.assertEqual(self.backend.get_conn_parameter("name"), self.backend.name)

    def test_input_files_picked_up_from_test_dir(self):
        """With test mode on, pending files are read from test dirs."""
        self.exchange_type_in.exchange_filename_pattern = ""
        self.backend.test_mode = True
        self.backend.test_input_dir_pending = "/test_input_test/pending/"
        input_dir = "/test_input_test/pending/"
        file_names = ["test-file-001.csv"]
        mocked_paths = {
            input_dir: "/tmp/",
            self._file_fullpath(
                "pending", fname=file_names[0], record=self.record_input
            ): self.fakepath_input_pending_1,
        }
        existing_records = self.env["edi.exchange.record"].search(
            [
                ("backend_id", "=", self.backend.id),
                ("type_id", "=", self.exchange_type_in.id),
            ]
        )
        found_files = [input_dir + fname for fname in file_names]
        with self._mock_fs_storage_find_files(found_files):
            self._test_run_cron_pending_input(mocked_paths)
        new_records = self.env["edi.exchange.record"].search(
            [
                ("backend_id", "=", self.backend.id),
                ("type_id", "=", self.exchange_type_in.id),
                ("id", "not in", existing_records.ids),
            ]
        )
        self.assertEqual(len(new_records), 1)
        self.assertEqual(new_records.exchange_filename, file_names[0])
        self.assertEqual(new_records.edi_exchange_state, "input_pending")
