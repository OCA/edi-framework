# Copyright 2024 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


import base64

from odoo.tests.common import RecordCapturer

from odoo.addons.edi_oca.tests.common import EDIBackendCommonComponentRegistryTestCase
from odoo.addons.edi_oca.tests.fake_components import FakeInputProcess


class TestEDINotification(EDIBackendCommonComponentRegistryTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_env()
        cls._build_components(
            cls,
            FakeInputProcess,
        )
        cls._load_module_components(cls, "edi_notification_oca")
        vals = {
            "model": cls.partner._name,
            "res_id": cls.partner.id,
            "exchange_file": base64.b64encode(b"1234"),
        }
        cls.record = cls.backend.create_record("test_csv_input", vals)
        cls.group_portal = cls.env.ref("base.group_portal")
        cls.user_a = cls._create_user(cls, "A")
        cls.user_b = cls._create_user(cls, "B")
        cls.user_c = cls._create_user(cls, "C")

    def setUp(self):
        super().setUp()
        FakeInputProcess.reset_faked()

    def _create_user(self, letter):
        return (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "User %s" % letter,
                    "login": "user_%s" % letter,
                    "groups_id": [(6, 0, [self.group_portal.id])],
                }
            )
        )

    def test_inverse_notify_on_process_error(self):
        self.exchange_type_in.notify_on_process_error = False
        # If we forgot to enable notify_on_process_error
        self.exchange_type_in.write(
            {
                "notify_on_process_error_groups_ids": [(6, 0, [self.group_portal.id])],
                "notify_on_process_error_users_ids": [(6, 0, [self.user_c.id])],
            }
        )
        # Make sure notify_on_process_error should be enabled
        self.assertTrue(self.exchange_type_in.notify_on_process_error)

    def test_dont_notify_on_process_error(self):
        self.exchange_type_in.notify_on_process_error = False
        self.record.write({"edi_exchange_state": "input_received"})
        self.record._set_file_content("TEST %d" % self.record.id)
        with RecordCapturer(self.env["mail.activity"], []) as capture:
            self.record.with_context(
                test_break_process="OOPS! Something went wrong :("
            ).action_exchange_process()
        self.assertRecordValues(
            self.record,
            [
                {
                    "edi_exchange_state": "input_processed_error",
                }
            ],
        )
        self.assertIn("OOPS! Something went wrong :(", self.record.exchange_error)
        # We don't expect any notification
        self.assertEqual(len(capture.records), 0)

    def test_notify_on_process_error_to_group(self):
        self.exchange_type_in.write(
            {
                "notify_on_process_error": True,
                "notify_on_process_error_groups_ids": [(6, 0, [self.group_portal.id])],
            }
        )
        # Remove group on user C to test
        self.user_c.groups_id = None
        self.record.write({"edi_exchange_state": "input_received"})
        self.record._set_file_content("TEST %d" % self.record.id)
        with RecordCapturer(self.env["mail.activity"], []) as capture:
            self.record.with_context(
                test_break_process="OOPS! Something went wrong :("
            ).action_exchange_process()
        # Send notification to all users in defined groups when error
        a_noti = capture.records.filtered(lambda x: x.user_id == self.user_a)
        self.assertEqual(len(a_noti), 1)
        self.assertEqual(
            a_noti.summary,
            f"EDI: Process error on record '{self.record.identifier}'.",
        )
        self.assertIn(
            "OOPS! Something went wrong :(",
            a_noti.note,
        )
        b_noti = capture.records.filtered(lambda x: x.user_id == self.user_b)
        self.assertEqual(len(a_noti), 1)
        self.assertEqual(
            b_noti.summary,
            f"EDI: Process error on record '{self.record.identifier}'.",
        )
        self.assertIn(
            "OOPS! Something went wrong :(",
            b_noti.note,
        )
        # We don't send notification to user C
        # because C is not belonging to the group_portal
        c_noti = capture.records.filtered(lambda x: x.user_id == self.user_c)
        self.assertEqual(len(c_noti), 0)

    def test_notify_on_process_error_to_users(self):
        self.exchange_type_in.write(
            {
                "notify_on_process_error": True,
                "notify_on_process_error_users_ids": [(6, 0, [self.user_c.id])],
            }
        )
        self.record.write({"edi_exchange_state": "input_received"})
        self.record._set_file_content("TEST %d" % self.record.id)
        with RecordCapturer(self.env["mail.activity"], []) as capture:
            self.record.with_context(
                test_break_process="OOPS! Something went wrong :("
            ).action_exchange_process()
        # Send notification to all users in defined users when error
        a_b_noti = capture.records.filtered(
            lambda x: x.user_id in (self.user_a | self.user_b)
        )
        self.assertEqual(len(a_b_noti), 0)
        c_noti = capture.records.filtered(lambda x: x.user_id == self.user_c)
        self.assertEqual(len(c_noti), 1)
        self.assertEqual(
            c_noti.summary,
            f"EDI: Process error on record '{self.record.identifier}'.",
        )
        self.assertIn(
            "OOPS! Something went wrong :(",
            c_noti.note,
        )

    def test_notify_on_process_error_to_groups_and_users(self):
        self.exchange_type_in.write(
            {
                "notify_on_process_error": True,
                "notify_on_process_error_groups_ids": [(6, 0, [self.group_portal.id])],
                "notify_on_process_error_users_ids": [(6, 0, [self.user_c.id])],
            }
        )
        # Remove group on user C to test
        self.user_c.groups_id = None
        self.record.write({"edi_exchange_state": "input_received"})
        self.record._set_file_content("TEST %d" % self.record.id)
        with RecordCapturer(self.env["mail.activity"], []) as capture:
            self.record.with_context(
                test_break_process="OOPS! Something went wrong :("
            ).action_exchange_process()
        # Send notification to all users in defined users when error
        a_b_noti = capture.records.filtered(
            lambda x: x.user_id in (self.user_a | self.user_b)
        )
        self.assertEqual(len(a_b_noti), 2)
        # also send notification to user C
        c_noti = capture.records.filtered(lambda x: x.user_id == self.user_c)
        self.assertEqual(len(c_noti), 1)
