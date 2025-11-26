# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from freezegun import freeze_time
from odoo_test_helper import FakeModelLoader

from odoo.addons.edi_core_oca.exceptions import EDINotImplementedError

from .common import EDIBackendCommonTestCase


class EDIBackendTestCaseBase(EDIBackendCommonTestCase):
    @classmethod
    def _setup_records(cls):  # pylint:disable=missing-return
        super()._setup_records()
        # Load fake models ->/
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .fake_models import EdiTestExecution

        cls.loader.update_registry((EdiTestExecution,))
        cls.ExecutionAbstractModel = cls.env["edi.framework.test.execution"]
        cls.model = cls.env["ir.model"]._get("edi.framework.test.execution")
        cls.exchange_type_in.receive_model_id = cls.model
        cls.exchange_type_in.process_model_id = cls.model
        cls.exchange_type_in.input_validate_model_id = cls.model

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    @freeze_time("2020-10-21 10:00:00")
    def test_create_record(self):
        self.env.user.tz = None  # Have no timezone used in generated filename
        vals = {
            "model": self.partner._name,
            "res_id": self.partner.id,
        }
        record = self.backend.create_record("test_csv_input", vals)
        expected = {
            "type_id": self.exchange_type_in.id,
            "edi_exchange_state": "new",
            "exchange_filename": "EDI_EXC_TEST-test_csv_"
            "input-2020-10-21-10-00-00.csv",
        }
        self.assertRecordValues(record, [expected])
        self.assertEqual(record.record, self.partner)
        self.assertEqual(record.edi_exchange_state, "new")

    def test_action_view_exchanges(self):
        # Just testing is not broken
        self.assertTrue(self.backend.action_view_exchanges())

    def test_action_view_exchange_types(self):
        # Just testing is not broken
        self.assertTrue(self.backend.action_view_exchange_types())

    def _test_get_handler(self, user=None):
        backend = self.backend
        if user:
            backend = self.backend.with_user(user)
        vals = {
            "model": self.partner._name,
            "res_id": self.partner.id,
        }
        record = backend.create_record("test_csv_input", vals)
        for action in ["receive", "input_validate", "process"]:
            self.assertEqual(
                str(backend._get_exec_handler(record, action)),
                str(getattr(self.ExecutionAbstractModel, action)),
            )

    def test_get_handler_admin(self):
        self._test_get_handler()

    def test_get_handler_avg_user(self):
        user = (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create({"name": "Test User EDI", "login": "test_edi_perm_user"})
        )
        self._test_get_handler(user=user)

    def test_get_handler_no_handler(self):
        self.exchange_type_in.process_model_id = False
        self.exchange_type_in.input_validate_model_id = False
        self.exchange_type_in.receive_model_id = False
        vals = {
            "model": self.partner._name,
            "res_id": self.partner.id,
        }
        record = self.backend.create_record("test_csv_input", vals)
        for action in ["receive", "input_validate", "process"]:
            with self.assertRaises(EDINotImplementedError):
                self.backend._get_exec_handler(record, action)
