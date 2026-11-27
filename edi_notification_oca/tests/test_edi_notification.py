# Copyright 2024 Camptocamp SA
# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


import base64

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests.common import RecordCapturer

from odoo.addons.edi_core_oca.tests.common import EDIBackendCommonTestCase


class TestEDINotificationCommon(EDIBackendCommonTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_env()
        cls.Rule = cls.env["edi.notification.rule"]
        cls.Trigger = cls.env["edi.notification.trigger"]

    @classmethod
    def _create_rule(cls, exchange_type, codes, **kw):
        vals = {
            "name": "Test rule",
            "type_id": exchange_type.id,
            "trigger_ids": [
                Command.set(cls.Trigger.search([("code", "in", codes)]).ids)
            ],
        }
        vals.update(kw)
        return cls.Rule.create(vals)


class TestEDINotificationDefaultRule(TestEDINotificationCommon):
    def _trigger_codes(self, exchange_type):
        rules = exchange_type.notification_rule_ids
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules.notification_type, "message")
        return set(rules.trigger_ids.mapped("code"))

    def test_default_rule_output(self):
        self.assertEqual(
            self._trigger_codes(self.exchange_type_out),
            {"generate_ok", "send_ok", "process_ok", "ack_received"},
        )

    def test_default_rule_input(self):
        self.assertEqual(
            self._trigger_codes(self.exchange_type_in),
            {"receive_ok", "process_ok"},
        )

    def test_no_default_rule_when_created_with_note_rule(self):
        trigger = self.env.ref("edi_notification_oca.trigger_send_ok")
        exchange_type = self._create_exchange_type(
            name="With rule",
            code="test_with_rule",
            direction="output",
            notification_rule_ids=[
                Command.create(
                    {
                        "name": "Sent only",
                        "notification_type": "message",
                        "trigger_ids": [Command.set(trigger.ids)],
                    }
                )
            ],
        )
        self.assertEqual(self._trigger_codes(exchange_type), {"send_ok"})

    def test_no_default_rule_with_skip_context(self):
        exchange_type = self.exchange_type_out.with_context(
            edi_notification_skip_default_rule=True
        ).copy({"code": "test_skip_default_rule"})
        self.assertFalse(exchange_type.notification_rule_ids)

    def test_post_init_hook_creates_missing_rules(self):
        self.exchange_type_out.notification_rule_ids.unlink()
        self.exchange_type_out._create_default_notification_rules()
        self.assertEqual(
            self._trigger_codes(self.exchange_type_out),
            {"generate_ok", "send_ok", "process_ok", "ack_received"},
        )

    def test_note_rule_rejects_error_trigger(self):
        with self.assertRaises(ValidationError):
            self._create_rule(self.exchange_type_out, ["send_ko"])

    def test_rule_rejects_other_direction_trigger(self):
        with self.assertRaises(ValidationError):
            self._create_rule(self.exchange_type_out, ["receive_ok"])

    def test_activity_rule_accepts_error_trigger(self):
        rule = self._create_rule(
            self.exchange_type_out,
            ["send_ko"],
            notification_type="activity",
            user_ids=[Command.set(self.env.ref("base.user_admin").ids)],
        )
        self.assertEqual(rule.trigger_ids.code, "send_ko")


class TestEDINotificationMessage(TestEDINotificationCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.record = cls.backend.create_record(
            "test_csv_output",
            {"model": cls.partner._name, "res_id": cls.partner.id},
        )
        cls.default_rule = cls.exchange_type_out.notification_rule_ids

    def _new_notes(self, before):
        return (self.partner.message_ids - before).filtered(
            lambda msg: "edi-exchange" in msg.body
        )

    def _notify_flow(self):
        """Generate and send, ending in a send error, then acknowledgements."""
        self.record.notify_action_complete(
            "generate", message=self.record._exchange_status_message("generate_ok")
        )
        self.record.notify_action_complete(
            "send", message=self.record._exchange_status_message("send_ok")
        )
        self.record._notify_error("send_ko")
        self.record._notify_ack_received()
        self.record._notify_ack_missing()

    def test_default_rule_posts_every_note(self):
        before = self.partner.message_ids
        self._notify_flow()
        self.assertEqual(len(self._new_notes(before)), 5)

    def test_status_removed_from_rule_not_posted(self):
        self.default_rule.trigger_ids -= self.env.ref(
            "edi_notification_oca.trigger_generate_ok"
        )
        before = self.partner.message_ids
        self.record.notify_action_complete(
            "generate", message=self.record._exchange_status_message("generate_ok")
        )
        self.assertFalse(self._new_notes(before))
        self.record.notify_action_complete("send", message="Sent!")
        notes = self._new_notes(before)
        self.assertEqual(len(notes), 1)
        self.assertIn("Sent!", notes.body)

    def test_inactive_rule_only_errors_posted(self):
        self.default_rule.active = False
        before = self.partner.message_ids
        self._notify_flow()
        self.record._notify_done()
        for code in ("validate_ko", "process_ko"):
            self.record._notify_error(code)
        self.record._notify_ack_received_error()
        notes = self._new_notes(before)
        # send_ko, ack_missing, validate_ko, process_ko, ack_received_error
        self.assertEqual(len(notes), 5)

    def test_status_without_trigger_posted(self):
        self.default_rule.unlink()
        before = self.partner.message_ids
        self.record._notify_state("custom_status", message="Custom status")
        self.assertEqual(len(self._new_notes(before)), 1)

    def test_other_type_rule_ignored(self):
        self.default_rule.active = False
        self._create_rule(self.exchange_type_in, ["process_ok"])
        before = self.partner.message_ids
        self.record._notify_done()
        self.assertFalse(self._new_notes(before))

    def test_activity_rule_does_not_post_note(self):
        self.default_rule.trigger_ids -= self.env.ref(
            "edi_notification_oca.trigger_send_ok"
        )
        self._create_rule(
            self.exchange_type_out,
            ["send_ok"],
            notification_type="activity",
            user_ids=[Command.set(self.env.ref("base.user_admin").ids)],
        )
        before = self.partner.message_ids
        with RecordCapturer(self.env["mail.activity"], []) as capture:
            self.record.notify_action_complete("send", message="Sent!")
        self.assertFalse(self._new_notes(before))
        self.assertEqual(len(capture.records), 1)
        self.assertEqual(capture.records.note, "<p>Sent!</p>")
        self.assertEqual(
            capture.records.summary,
            f"EDI: Sent on record '{self.record.identifier}'.",
        )


class TestEDINotificationActivity(TestEDINotificationCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        vals = {
            "model": cls.partner._name,
            "res_id": cls.partner.id,
            "exchange_file": base64.b64encode(b"1234"),
        }
        cls.record = cls.backend.create_record("test_csv_input", vals)
        cls.group_portal = cls.env.ref("base.group_portal")
        cls.user_a = cls._create_user("A")
        cls.user_b = cls._create_user("B")
        cls.user_c = cls._create_user("C")

    @classmethod
    def _create_user(cls, letter: str):
        return (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": f"User {letter}",
                    "login": f"user_{letter}",
                    "group_ids": [Command.set([cls.group_portal.id])],
                }
            )
        )

    def _create_error_rule(self, **kw):
        return self._create_rule(
            self.exchange_type_in, ["process_ko"], notification_type="activity", **kw
        )

    def _trigger_process_error(self, message="OOPS! Something went wrong :("):
        self.record.exchange_error = message
        self.record._notify_error("process_ko")

    def test_activity_rule_requires_targets(self):
        with self.assertRaises(ValidationError):
            self._create_error_rule()

    def test_no_rule_no_activity(self):
        with RecordCapturer(self.env["mail.activity"], []) as capture:
            self._trigger_process_error()
        self.assertFalse(capture.records)

    def test_inactive_rule_no_activity(self):
        self._create_error_rule(user_ids=[Command.set(self.user_c.ids)], active=False)
        with RecordCapturer(self.env["mail.activity"], []) as capture:
            self._trigger_process_error()
        self.assertFalse(capture.records)

    def test_rule_other_trigger_no_activity(self):
        self._create_error_rule(user_ids=[Command.set(self.user_c.ids)])
        with RecordCapturer(self.env["mail.activity"], []) as capture:
            self.record.exchange_error = "Send failed"
            self.record._notify_error("send_ko")
        self.assertFalse(capture.records)

    def test_activity_to_group(self):
        self._create_error_rule(group_ids=[Command.set(self.group_portal.ids)])
        self.user_c.group_ids = [Command.clear()]
        with RecordCapturer(self.env["mail.activity"], []) as capture:
            self._trigger_process_error()
        activities = capture.records.filtered(
            lambda act: act.user_id in self.user_a | self.user_b | self.user_c
        )
        self.assertEqual(activities.user_id, self.user_a | self.user_b)
        self.assertEqual(len(activities), 2)
        for activity in activities:
            self.assertEqual(
                activity.summary,
                f"EDI: Process error on record '{self.record.identifier}'.",
            )
            self.assertIn("OOPS! Something went wrong :(", activity.note)
            self.assertEqual(
                activity.activity_type_id,
                self.env.ref(
                    "edi_notification_oca.mail_activity_failed_exchange_record_warning"
                ),
            )

    def test_activity_to_users(self):
        self._create_error_rule(user_ids=[Command.set(self.user_c.ids)])
        with RecordCapturer(self.env["mail.activity"], []) as capture:
            self._trigger_process_error()
        self.assertEqual(capture.records.user_id, self.user_c)
        self.assertIn("OOPS! Something went wrong :(", capture.records.note)

    def test_activity_to_groups_and_users(self):
        self._create_error_rule(
            group_ids=[Command.set(self.group_portal.ids)],
            user_ids=[Command.set(self.user_c.ids)],
        )
        self.user_c.group_ids = [Command.clear()]
        with RecordCapturer(self.env["mail.activity"], []) as capture:
            self._trigger_process_error()
        activities = capture.records.filtered(
            lambda act: act.user_id in self.user_a | self.user_b | self.user_c
        )
        self.assertEqual(activities.user_id, self.user_a | self.user_b | self.user_c)
        self.assertEqual(len(activities), 3)

    def test_activity_to_implied_group_users(self):
        group_user = self.env.ref("base.group_user")
        user_d = self._create_user("D")
        user_d.group_ids = [Command.set(self.env.ref("base.group_system").ids)]
        self.assertNotIn(user_d, group_user.user_ids)
        self._create_error_rule(group_ids=[Command.set(group_user.ids)])
        with RecordCapturer(self.env["mail.activity"], []) as capture:
            self._trigger_process_error()
        self.assertIn(user_d, capture.records.user_id)

    def test_activity_error_note_still_posted(self):
        self.exchange_type_in.notification_rule_ids.active = False
        self._create_error_rule(user_ids=[Command.set(self.user_c.ids)])
        before = self.partner.message_ids
        self._trigger_process_error()
        notes = (self.partner.message_ids - before).filtered(
            lambda msg: "edi-exchange" in msg.body
        )
        self.assertEqual(len(notes), 1)
        self.assertIn("level-error", notes.body)
