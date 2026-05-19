# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64
from unittest import mock

from odoo_test_helper import FakeModelLoader

from odoo.addons.edi_core_oca.tests.common import EDIBackendCommonTestCase
from odoo.addons.edi_core_oca.tests.fake_models import EdiTestExecution

STORAGE_MOVE_FILE_PATH = "odoo.addons.edi_storage_oca.utils.move_file"


class TestStorageEventListener(EDIBackendCommonTestCase):
    @classmethod
    def _get_backend(cls):
        return cls.env.ref("edi_storage_oca.demo_edi_backend_storage")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.conf_done = cls.env.ref("edi_storage_oca.edi_conf_storage_move_on_done")
        cls.conf_error = cls.env.ref("edi_storage_oca.edi_conf_storage_move_on_error")
        (cls.conf_done | cls.conf_error).write(
            {"active": True, "backend_id": cls.backend.id}
        )

        vals = {
            "model": cls.partner._name,
            "res_id": cls.partner.id,
            "exchange_file": base64.b64encode(b"1234"),
            "storage_id": cls.backend.storage_id.id,
        }
        cls.record = cls.backend.create_record("test_csv_input", vals)

    def setUp(self):
        super().setUp()
        self.loader = FakeModelLoader(self.env, self.__module__)
        self.loader.backup_registry()

        self.loader.update_registry((EdiTestExecution,))
        fake_model = self.env["ir.model"].search(
            [("model", "=", "edi.framework.test.execution")]
        )
        self.exchange_type_in.process_model_id = fake_model
        self.exchange_type_in.input_validate_model_id = fake_model

    def tearDown(self):
        self.loader.restore_registry()
        super().tearDown()

    def _patch_move_file(self):
        return mock.patch(STORAGE_MOVE_FILE_PATH, autospec=True, return_value=True)

    def _expected_dir(self, raw_dir):
        return self.exchange_type_in._storage_fullpath(raw_dir).as_posix()

    def test_01_process_record_success(self):
        self.record.write({"edi_exchange_state": "input_received"})
        with self._patch_move_file() as mocked:
            self.record.action_exchange_process()
        mocked.assert_called_once()
        storage, from_dir_str, to_dir_str, filename = mocked.call_args[0]
        self.assertEqual(storage, self.backend.storage_id)
        self.assertEqual(
            from_dir_str, self._expected_dir(self.backend.input_dir_pending)
        )
        self.assertEqual(to_dir_str, self._expected_dir(self.backend.input_dir_done))
        self.assertEqual(filename, self.record.exchange_filename)

    def test_02_process_record_with_error(self):
        self.record.write({"edi_exchange_state": "input_received"})
        self.record._set_file_content("TEST %d" % self.record.id)
        with self._patch_move_file() as mocked:
            self.record.with_context(
                test_break_process="OOPS! Something went wrong :("
            ).action_exchange_process()
        mocked.assert_called_once()
        storage, from_dir_str, to_dir_str, filename = mocked.call_args[0]
        self.assertEqual(storage, self.backend.storage_id)
        self.assertEqual(
            from_dir_str, self._expected_dir(self.backend.input_dir_pending)
        )
        self.assertEqual(to_dir_str, self._expected_dir(self.backend.input_dir_error))
        self.assertEqual(filename, self.record.exchange_filename)
