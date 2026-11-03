# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from unittest import mock

from .common import EDIBackendCommonTestCase


class TestNotifyState(EDIBackendCommonTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.record = cls.backend.create_record(
            "test_csv_output",
            {"model": cls.partner._name, "res_id": cls.partner.id},
        )

    def _new_notes(self, before):
        return (self.partner.message_ids - before).filtered(
            lambda msg: "edi-exchange" in msg.body
        )

    def _patch_notify_state(self):
        return mock.patch.object(type(self.record), "_notify_state")

    def test_notify_state_default_message(self):
        before = self.partner.message_ids
        self.record._notify_state("send_ko", level="error")
        note = self._new_notes(before)
        self.assertEqual(len(note), 1)
        self.assertIn(self.record._exchange_status_message("send_ko"), note.body)
        self.assertIn("level-error", note.body)

    def test_notify_state_custom_message(self):
        before = self.partner.message_ids
        self.record._notify_state("send_ok", message="Custom message")
        note = self._new_notes(before)
        self.assertEqual(len(note), 1)
        self.assertIn("Custom message", note.body)

    def test_notify_action_complete(self):
        with self._patch_notify_state() as mocked:
            self.record.notify_action_complete("send", message="Sent!")
        mocked.assert_called_once_with("send_ok", message="Sent!")

    def test_notify_action_complete_without_message(self):
        with self._patch_notify_state() as mocked:
            self.record.notify_action_complete("process")
        mocked.assert_not_called()

    def test_notify_done(self):
        with self._patch_notify_state() as mocked:
            self.record._notify_done()
        mocked.assert_called_once_with("process_ok")

    def test_notify_error(self):
        with self._patch_notify_state() as mocked:
            self.record._notify_error("process_ko")
        mocked.assert_called_once_with("process_ko", level="error")

    def test_notify_ack(self):
        with self._patch_notify_state() as mocked:
            self.record._notify_ack_received()
            self.record._notify_ack_missing()
            self.record._notify_ack_received_error()
        self.assertEqual(
            mocked.call_args_list,
            [
                mock.call("ack_received"),
                mock.call("ack_missing", level="warning"),
                mock.call("ack_received_error"),
            ],
        )
