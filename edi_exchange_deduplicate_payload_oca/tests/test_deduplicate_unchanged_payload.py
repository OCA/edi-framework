# Copyright 2026 Camptocamp SA
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import json
from unittest.mock import patch

from odoo.orm.model_classes import add_to_registry
from odoo.tests import tagged

from odoo.addons.edi_core_oca.tests.common import EDIBackendCommonTestCase

UNCHANGED_MSG = "Nothing to send: payload already exported. Marked as obsolete."


@tagged("post_install", "-at_install")
class TestDeduplicateUnchangedPayload(EDIBackendCommonTestCase):
    """Do not send payloads already exported, on flagged exchange types."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_fake_models()
        cls.payload_model = cls.env["edi.payload.output"]
        cls.consumer_model = cls.env["edi.dedup.payload.consumer.test"]
        cls.record = cls.consumer_model.create({"name": "Rec"})
        cls.exchange_type_out.write(
            {
                "deduplicate_unchanged_payload": True,
                "exchange_filename_pattern": "{record.name}-{type.code}-{dt}",
                "exchange_file_ext": "json",
            }
        )
        cls.execution = cls.env["edi.framework.test.execution"]

    @classmethod
    def _setup_fake_models(cls):
        """Add the test consumer model to the registry, removed on cleanup."""
        from .fake_models import EDIDeduplicatePayloadConsumerTest

        model_name = EDIDeduplicatePayloadConsumerTest._name
        add_to_registry(cls.registry, EDIDeduplicatePayloadConsumerTest)
        cls.registry._setup_models__(cls.env.cr, [model_name])
        cls.registry.init_models(cls.env.cr, [model_name], {"models_to_check": True})
        cls.addClassCleanup(cls.registry.__delitem__, model_name)

    def setUp(self):
        super().setUp()
        self.execution.reset_faked("send")

    def _pending_exchange(self, payload, record=None):
        """Return an exchange record ready to send `payload` for `record`."""
        record = record or self.record
        exchange = self.backend.create_record(
            self.exchange_type_out.code,
            {"model": record._name, "res_id": record.id},
        )
        exchange._set_file_content(json.dumps(payload))
        exchange.edi_exchange_state = "output_pending"
        return exchange

    def test_nothing_stored_is_sent(self):
        """A record never exported is sent."""
        exchange = self._pending_exchange({"name": "Rec"})
        self.assertTrue(self.backend._output_check_send(exchange))
        self.backend.exchange_send(exchange)
        self.assertEqual(exchange.edi_exchange_state, "output_sent")
        self.assertTrue(self.execution.check_called_for(exchange, "send"))

    def test_changed_payload_is_sent(self):
        """A payload with a key holding a new value is sent."""
        self.record.edi_payload_set_output({"name": "Rec", "qty": 1})
        exchange = self._pending_exchange({"qty": 2})
        self.assertTrue(self.backend._output_check_send(exchange))
        self.backend.exchange_send(exchange)
        self.assertEqual(exchange.edi_exchange_state, "output_sent")

    def test_new_key_is_sent(self):
        """A payload with a key not stored yet is sent."""
        self.record.edi_payload_set_output({"name": "Rec"})
        exchange = self._pending_exchange({"name": "Rec", "qty": 1})
        self.assertTrue(self.backend._output_check_send(exchange))

    def test_unchanged_payload_is_obsolete(self):
        """A payload already exported is not sent and becomes obsolete."""
        self.record.edi_payload_set_output({"name": "Rec", "qty": 1})
        exchange = self._pending_exchange({"qty": 1})
        self.assertFalse(self.backend._output_check_send(exchange))
        result = self.backend.exchange_send(exchange)
        self.assertEqual(result, UNCHANGED_MSG)
        self.assertEqual(exchange.edi_exchange_state, "obsolete")
        self.assertFalse(self.execution.check_called_for(exchange, "send"))

    def test_deleted_record_is_obsolete(self):
        """The payload of a record deleted meanwhile is not sent."""
        other = self.consumer_model.create({"name": "Gone"})
        exchange = self._pending_exchange({"name": "Gone"}, record=other)
        other.unlink()
        self.assertEqual(self.backend.exchange_send(exchange), UNCHANGED_MSG)
        self.assertEqual(exchange.edi_exchange_state, "obsolete")

    def test_flag_off_sends_unchanged(self):
        """Without the flag, an unchanged payload is sent as usual."""
        self.exchange_type_out.deduplicate_unchanged_payload = False
        self.record.edi_payload_set_output({"qty": 1})
        exchange = self._pending_exchange({"qty": 1})
        self.backend.exchange_send(exchange)
        self.assertEqual(exchange.edi_exchange_state, "output_sent")

    def test_already_sent_is_left_alone(self):
        """A record not pending is neither sent nor made obsolete."""
        self.record.edi_payload_set_output({"qty": 1})
        exchange = self._pending_exchange({"qty": 1})
        exchange.edi_exchange_state = "output_sent"
        self.backend.exchange_send(exchange)
        self.assertEqual(exchange.edi_exchange_state, "output_sent")

    def test_store_then_resend_is_obsolete(self):
        """Once stored, the same payload is skipped on the next export."""
        first = self._pending_exchange({"name": "Rec", "qty": 1})
        self.backend.exchange_send(first)
        self.record.edi_payload_set_output({"name": "Rec", "qty": 1})
        second = self._pending_exchange({"qty": 1})
        self.backend.exchange_send(second)
        self.assertEqual(second.edi_exchange_state, "obsolete")

    def test_model_without_tracking_is_sent(self):
        """A record whose model does not track its payload is sent as usual."""
        exchange = self.backend.create_record(
            self.exchange_type_out.code,
            {"model": self.partner._name, "res_id": self.partner.id},
        )
        exchange._set_file_content(json.dumps({"name": self.partner.name}))
        exchange.edi_exchange_state = "output_pending"
        self.assertTrue(self.backend._output_check_send(exchange))
        self.backend.exchange_send(exchange)
        self.assertEqual(exchange.edi_exchange_state, "output_sent")

    def test_model_comparison_is_used(self):
        """The comparison of the record's model decides."""
        self.record.edi_payload_set_output({"qty": 1})
        exchange = self._pending_exchange({"qty": 2})
        with patch.object(
            type(self.consumer_model), "_edi_payload_has_changes", return_value=False
        ) as has_changes:
            self.backend.exchange_send(exchange)
        has_changes.assert_called_once_with({"qty": 2})
        self.assertEqual(exchange.edi_exchange_state, "obsolete")
