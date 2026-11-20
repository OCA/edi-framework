# Copyright 2026 Camptocamp SA
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.exceptions import ValidationError
from odoo.orm.model_classes import add_to_registry
from odoo.tests import new_test_user, tagged

from odoo.addons.edi_core_oca.tests.common import EDIBackendCommonTestCase

LOCKED_MSG = "This record is locked because it has already been sent."


@tagged("post_install", "-at_install")
class TestLockOutput(EDIBackendCommonTestCase):
    """Lock the listed fields of records once their output was sent."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_fake_models()
        cls.exchange_type_out.write(
            {
                "lock_record_on_send": True,
                "exchange_filename_pattern": "{record.name}-{type.code}-{dt}",
            }
        )
        cls.record = cls.env["edi.lock.output.consumer.test"].create(
            {"name": "Rec", "qty": 1}
        )
        # The superuser and the admin are in the bypass group: write as a
        # plain user. sudo() after with_user() skips the access rights of the
        # test model but keeps the user, whose groups the lock checks.
        cls.user = new_test_user(
            cls.env, login="edi_lock_output_user", groups="base.group_user"
        )
        cls.user_record = cls.record.with_user(cls.user).sudo()

    @classmethod
    def _setup_fake_models(cls):
        """Add the test model to the registry, removed on cleanup."""
        from .fake_models import EDILockOutputConsumerTest

        model_name = EDILockOutputConsumerTest._name
        add_to_registry(cls.registry, EDILockOutputConsumerTest)
        cls.registry._setup_models__(cls.env.cr, [model_name])
        cls.registry.init_models(cls.env.cr, [model_name], {"models_to_check": True})
        cls.addClassCleanup(cls.registry.__delitem__, model_name)

    def _exchange(self, state, exchange_type=None, record=None):
        """Create an exchange of the record in `state`."""
        exchange_type = exchange_type or self.exchange_type_out
        record = record or self.record
        exchange = self.backend.create_record(
            exchange_type.code,
            {"model": record._name, "res_id": record.id},
        )
        exchange.edi_exchange_state = state
        return exchange

    def test_not_sent_is_editable(self):
        """A record never sent can be changed."""
        self.user_record.write({"name": "New", "qty": 2})
        self.assertFalse(self.record._edi_lock_output_is_locked())

    def test_pending_is_editable(self):
        """A record whose exchange is not sent yet can be changed."""
        self._exchange("output_pending")
        self.user_record.qty = 2
        self.assertFalse(self.record._edi_lock_output_is_locked())

    def test_sent_is_locked(self):
        """Once sent, the locked fields can no longer be changed."""
        for state in (
            "output_sent",
            "output_sent_and_processed",
            "output_sent_and_error",
        ):
            with self.subTest(state=state):
                exchange = self._exchange(state)
                self.assertTrue(self.record._edi_lock_output_is_locked())
                with self.assertRaisesRegex(ValidationError, f"^{LOCKED_MSG}$"):
                    self.user_record.qty = 2
                exchange.unlink()

    def test_sent_other_fields_editable(self):
        """Fields not listed stay editable on a locked record."""
        self._exchange("output_sent")
        self.user_record.note = "Still editable"
        self.assertEqual(self.record.note, "Still editable")

    def test_type_not_flagged(self):
        """An exchange of a type not flagged does not lock the record."""
        self.exchange_type_out.lock_record_on_send = False
        self._exchange("output_sent")
        self.user_record.qty = 2
        self.assertEqual(self.record.qty, 2)

    def test_bypass_context(self):
        """The context key bypasses the lock."""
        self._exchange("output_sent")
        self.user_record.with_context(edi_lock_output_bypass=True).qty = 2
        self.assertEqual(self.record.qty, 2)

    def test_bypass_group(self):
        """Users of the bypass group can change locked fields."""
        self._exchange("output_sent")
        bypass_user = new_test_user(
            self.env,
            login="edi_lock_output_bypass",
            groups="base.group_user,edi_lock_output_oca.group_bypass_lock",
        )
        self.record.with_user(bypass_user).sudo().qty = 2
        self.assertEqual(self.record.qty, 2)
        with self.assertRaisesRegex(ValidationError, f"^{LOCKED_MSG}$"):
            self.user_record.qty = 3

    def test_lock_check_without_edi_access(self):
        """Users without access to EDI exchanges are locked out too."""
        self._exchange("output_sent")
        self.assertTrue(self.record.with_user(self.user)._edi_lock_output_is_locked())

    def test_locked_records(self):
        """Only the sent records are returned as locked, in one query."""
        other = self.record.create({"name": "Other", "qty": 1})
        self._exchange("output_sent", record=other)
        records = self.record | other
        # Leave only the search of the sent records to count: the override of
        # the test model reads the note.
        records.mapped("note")
        self.env.flush_all()
        with self.assertQueryCount(1):
            self.assertEqual(records._edi_lock_output_is_locked(), other)
        with self.assertRaisesRegex(ValidationError, f"^{LOCKED_MSG}$"):
            records.with_user(self.user).sudo().write({"qty": 2})

    def test_override_adds_locked_records(self):
        """An override locks its own records and keeps the sent ones locked."""
        other = self.record.create({"name": "Other", "qty": 1, "note": "frozen"})
        self._exchange("output_sent")
        records = self.record | other
        self.assertEqual(records._edi_lock_output_is_locked(), records)
        with self.assertRaisesRegex(ValidationError, f"^{LOCKED_MSG}$"):
            other.with_user(self.user).sudo().qty = 2
