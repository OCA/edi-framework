# Copyright 2026 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.edi_oca.tests.common import EDIBackendCommonComponentRegistryTestCase
from odoo.addons.edi_oca.tests.fake_components import (
    FakeOutputChecker,
    FakeOutputGenerator,
    FakeOutputSender,
)


class TestNotifyRelatedRecord(EDIBackendCommonComponentRegistryTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._build_components(
            cls,
            FakeOutputGenerator,
            FakeOutputSender,
            FakeOutputChecker,
        )
        cls.record = cls.backend.create_record(
            "test_csv_output",
            {"model": cls.partner._name, "res_id": cls.partner.id},
        )

    def setUp(self):
        super().setUp()
        FakeOutputGenerator.reset_faked()
        FakeOutputSender.reset_faked()
        FakeOutputChecker.reset_faked()

    def _new_messages(self, before):
        return self.partner.message_ids - before

    def test_notify_on_generate_default(self):
        before = self.partner.message_ids
        self.record.with_context(fake_output="yeah!").action_exchange_generate()
        messages = self._new_messages(before)
        self.assertEqual(len(messages), 1)
        self.assertIn("Exchange data generated", messages.body)

    def test_notify_on_generate_disabled(self):
        self.record.type_id.notify_related_record_on_generate = False
        before = self.partner.message_ids
        self.record.with_context(fake_output="yeah!").action_exchange_generate()
        # Generate no longer posts a note on the related record...
        self.assertFalse(self._new_messages(before))
        # ...but send still does.
        self.record.action_exchange_send()
        messages = self._new_messages(before)
        self.assertEqual(len(messages), 1)
        self.assertIn("Exchange sent", messages.body)

    def test_notify_on_send_disabled(self):
        self.record.type_id.notify_related_record_on_send = False
        self.record.with_context(fake_output="yeah!").action_exchange_generate()
        before = self.partner.message_ids
        self.record.action_exchange_send()
        self.assertFalse(self._new_messages(before))

    def test_notify_on_process_default(self):
        before = self.partner.message_ids
        self.record._notify_done()
        messages = self._new_messages(before)
        self.assertEqual(len(messages), 1)
        self.assertIn("Exchange processed successfully", messages.body)

    def test_notify_on_process_disabled(self):
        self.record.type_id.notify_related_record_on_process = False
        before = self.partner.message_ids
        self.record._notify_done()
        self.assertFalse(self._new_messages(before))
        self.record._notify_error("process_ko")
        self.assertFalse(self._new_messages(before))

    def test_notify_without_toggle_still_posts(self):
        """Actions with no dedicated toggle keep notifying (eg: acknowledgements)."""
        self.record.type_id.write(
            {
                "notify_related_record_on_generate": False,
                "notify_related_record_on_send": False,
                "notify_related_record_on_process": False,
                "notify_related_record_on_receive": False,
            }
        )
        before = self.partner.message_ids
        self.record._notify_ack_received()
        self.assertEqual(len(self._new_messages(before)), 1)
