# Copyright 2026 Camptocamp SA
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from unittest.mock import patch

from psycopg2.errors import UniqueViolation

from odoo.tests import new_test_user, tagged

from .common import PayloadTrackingTestCase


@tagged("post_install", "-at_install")
class TestEDIPayloadOutput(PayloadTrackingTestCase):
    """Store and read the payload exported for a record."""

    def test_get_payload_nothing_stored(self):
        """A record never exported has an empty payload."""
        self.assertEqual(self.record.edi_payload_get_output(), {})
        self.assertEqual(self.payload_model.get_payload(self.record), {})

    def test_set_payload_creates(self):
        """The first payload stored creates one row for the record."""
        stored = self.record.edi_payload_set_output({"name": "first"})
        self.assertEqual(stored.model_id.model, "edi.payload.consumer.test")
        self.assertEqual(stored.res_id, self.record.id)
        self.assertEqual(self.record.edi_payload_get_output(), {"name": "first"})

    def test_set_payload_replaces(self):
        """A new payload replaces the stored one, on the same row."""
        first = self.record.edi_payload_set_output({"name": "first", "a": 1})
        second = self.record.edi_payload_set_output({"name": "second"})
        self.assertEqual(first, second)
        self.assertEqual(self.record.edi_payload_get_output(), {"name": "second"})

    def test_set_payload_empty(self):
        """Storing no payload stores an empty dict."""
        self.record.edi_payload_set_output(None)
        self.assertEqual(self.record.edi_payload_get_output(), {})

    def test_payload_per_record(self):
        """Each record has its own payload."""
        self.record.edi_payload_set_output({"name": "one"})
        self.other_record.edi_payload_set_output({"name": "two"})
        self.assertEqual(self.record.edi_payload_get_output(), {"name": "one"})
        self.assertEqual(self.other_record.edi_payload_get_output(), {"name": "two"})

    def test_set_payload_created_concurrently(self):
        """A payload created concurrently raises, the transaction stays usable."""
        self.payload_model.set_payload(self.record, {"name": "first"})
        # A payload committed by a concurrent transaction after this one
        # started is not visible to it: the lookup misses it and the insert
        # collides with it. The default error is forced, as modules like
        # edi_payload_tracking_queue_oca replace it.
        model_class = type(self.payload_model)
        with (
            patch.object(
                model_class,
                "_find_for_record",
                return_value=self.payload_model.browse(),
            ),
            patch.object(
                model_class,
                "_payload_concurrent_create_error",
                lambda model, record, error: error,
            ),
            self.assertRaises(UniqueViolation),
        ):
            self.payload_model.set_payload(self.record, {"name": "second"})
        self.assertEqual(self.record.edi_payload_get_output(), {"name": "first"})

    def test_internal_user_can_store_payload(self):
        """An internal user can store and read the payload of a record."""
        user = new_test_user(self.env, login="edi_payload_user")
        record = self.record.with_user(user)
        record.edi_payload_set_output({"name": "by user"})
        self.assertEqual(record.edi_payload_get_output(), {"name": "by user"})
