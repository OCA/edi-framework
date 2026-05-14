# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import unittest

from odoo.orm.model_classes import add_to_registry

from .common import EDIBackendCommonTestCase


# This clashes w/ some setup (eg: run tests w/ pytest when edi_storage is installed)
# If you still want to run `edi` tests w/ pytest when this happens, set this env var.
@unittest.skipIf(os.getenv("SKIP_EDI_CONSUMER_CASE"), "Consumer test case disabled.")
class TestEDIConfigurations(EDIBackendCommonTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        vals = {
            "model": cls.partner._name,
            "res_id": cls.partner.id,
        }
        cls.record = cls.backend.create_record("test_csv_output", vals)

    def setUp(self):
        super().setUp()
        self.ExecutionAbstractModel.reset_faked("generate")
        self.ExecutionAbstractModel.reset_faked("send")
        self.ExecutionAbstractModel.reset_faked("check")
        self.consumer_record = self.env["edi.exchange.consumer.test"].create(
            {
                "name": "Test Consumer",
                "edi_config_ids": [
                    (4, self.create_config.id),
                    (4, self.write_config.id),
                ],
            }
        )

    @classmethod
    def _setup_records(cls):  # pylint:disable=missing-return
        super()._setup_records()
        # Load fake models ->/
        from .fake_models import EdiExchangeConsumerTest, EdiTestExecution

        add_to_registry(cls.registry, EdiTestExecution)
        add_to_registry(cls.registry, EdiExchangeConsumerTest)
        cls.registry._setup_models__(cls.env.cr, ["edi.exchange.consumer.test"])
        cls.registry.init_models(
            cls.env.cr, ["edi.exchange.consumer.test"], {"models_to_check": True}
        )
        cls.registry._setup_models__(cls.env.cr, ["edi.framework.test.execution"])
        cls.registry.init_models(
            cls.env.cr, ["edi.framework.test.execution"], {"models_to_check": True}
        )
        cls.addClassCleanup(cls.registry.__delitem__, "edi.framework.test.execution")
        cls.addClassCleanup(cls.registry.__delitem__, "edi.exchange.consumer.test")
        cls.ExecutionAbstractModel = cls.env["edi.framework.test.execution"]
        cls.model = cls.env["ir.model"]._get("edi.framework.test.execution")
        cls.exchange_type_out.generate_model_id = cls.model
        cls.exchange_type_out.send_model_id = cls.model
        cls.exchange_type_out.exchange_filename_pattern = "{record.id}"
        cls.edi_configuration = cls.env["edi.configuration"]
        cls.create_trigger = cls.env.ref("edi_core_oca.edi_conf_trigger_record_create")
        cls.write_trigger = cls.env.ref("edi_core_oca.edi_conf_trigger_record_write")
        cls.create_config = cls.edi_configuration.create(
            {
                "name": "Create Config",
                "active": True,
                "backend_id": cls.backend.id,
                "type_id": cls.exchange_type_out.id,
                "trigger_id": cls.create_trigger.id,
                "model_id": cls.env["ir.model"]._get_id("edi.exchange.consumer.test"),
                "snippet_do": "record._edi_send_via_edi(conf.type_id)",
            }
        )
        cls.write_config = cls.edi_configuration.create(
            {
                "name": "Write Config 1",
                "active": True,
                "backend_id": cls.backend.id,
                "type_id": cls.exchange_type_out.id,
                "trigger_id": cls.write_trigger.id,
                "model_id": cls.env["ir.model"]._get_id("edi.exchange.consumer.test"),
                "snippet_do": "record._edi_send_via_edi(conf.type_id)",
            }
        )

    def test_edi_send_via_edi_config(self):
        # Check configuration on create
        self.consumer_record.invalidate_recordset()
        exchange_record = self.consumer_record.exchange_record_ids
        self.assertEqual(len(exchange_record), 1)
        self.assertEqual(exchange_record.type_id, self.exchange_type_out)
        self.assertEqual(exchange_record.edi_exchange_state, "output_sent")
        # Write the existed consumer record
        self.consumer_record.name = "Fixed Consumer"
        # check Configuration on write
        self.consumer_record.invalidate_recordset()
        exchange_record = self.consumer_record.exchange_record_ids - exchange_record
        self.assertEqual(len(exchange_record), 1)
        self.assertEqual(exchange_record.type_id, self.exchange_type_out)
        self.assertEqual(exchange_record.edi_exchange_state, "output_sent")

    def test_edi_code_snippet(self):
        expected_value = {
            "todo": True,
            "snippet_do_vars": {
                "a": 1,
                "b": 2,
            },
            "event_only": True,
            "tracked_fields": ["state"],
            "edi_action": "new_action",
        }
        # Simulate the snippet_before_do
        self.write_config.snippet_before_do = "result = " + str(expected_value)
        # Execute with the raw data
        vals = self.write_config.edi_exec_snippet_before_do(
            self.consumer_record,
            tracked_fields=[],
            edi_action="generate",
        )
        # Check the new vals after execution
        expected_value["conf"] = self.write_config
        self.assertEqual(vals, expected_value)

        # Check the snippet_do
        expected_value = {
            "change_state": True,
            "snippet_do_vars": {
                "a": 1,
                "b": 2,
            },
            "record": self.consumer_record,
            "tracked_fields": ["state"],
        }
        snippet_do = """\n
old_state = old_value.get("state", False)\n
new_state = vals.get("state", False)\n
change_state = True if old_state and new_state and old_state != new_state else False
result = {\n
    "change_state": change_state,\n
    "snippet_do_vars": snippet_do_vars,\n
    "record": record,\n
    "tracked_fields": tracked_fields,\n
}
        """
        self.write_config.snippet_do = snippet_do
        # Execute with the raw data
        record_id = self.consumer_record.id
        vals = self.write_config.edi_exec_snippet_do(
            self.consumer_record,
            tracked_fields=[],
            edi_action="generate",
            old_vals={record_id: dict(state="draft")},
            vals={record_id: dict(state="confirmed")},
        )
        # Check the new vals after execution
        self.assertEqual(vals, expected_value)


class TestEDIConfigurationGlobalEvents(EDIBackendCommonTestCase):
    """Test the global event dispatch via edi.configuration.

    `EDIExchangeRecord._trigger_edi_event` looks up all `edi.configuration`
    records flagged as `is_global` and matching the event trigger code,
    then executes their `snippet_do` against the target record.
    These tests verify the dispatch happens for all `notify_*` events
    and that the proper target (exchange record vs related record)
    is passed to the snippet.
    """

    # Snippet appends a marker per call so we can verify multiple invocations
    # against different targets within the same transaction.
    _marker_snippet = (
        "conf.write({'description': (conf.description or '') + '|' + record._name})"
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        vals = {
            "model": cls.partner._name,
            "res_id": cls.partner.id,
        }
        cls.record = cls.backend.create_record("test_csv_output", vals)
        cls.trigger_model = cls.env["edi.configuration.trigger"]
        cls.conf_model = cls.env["edi.configuration"]
        # Reuse existing data triggers when available, create the missing ones.
        cls.trigger_done = cls.env.ref("edi_core_oca.edi_config_trigger_record_done")
        cls.trigger_error = cls.env.ref("edi_core_oca.edi_config_trigger_record_error")
        cls.trigger_ack_received = cls._get_or_create_trigger(
            "on_edi_exchange_done_ack_received", "On ACK received"
        )
        cls.trigger_ack_missing = cls._get_or_create_trigger(
            "on_edi_exchange_done_ack_missing", "On ACK missing"
        )
        cls.trigger_ack_received_error = cls._get_or_create_trigger(
            "on_edi_exchange_done_ack_received_error", "On ACK received error"
        )
        cls.trigger_generate_complete = cls._get_or_create_trigger(
            "on_edi_exchange_generate_complete", "On generate complete"
        )

    @classmethod
    def _get_or_create_trigger(cls, code, name):
        trigger = cls.trigger_model.search([("code", "=", code)], limit=1)
        if not trigger:
            trigger = cls.trigger_model.create({"name": name, "code": code})
        return trigger

    def _make_conf(self, trigger, name, is_global=True, snippet=None, **overrides):
        vals = {
            "name": name,
            "active": True,
            "backend_id": self.backend.id,
            "type_id": self.exchange_type_out.id,
            "trigger_id": trigger.id,
            "is_global": is_global,
            "snippet_do": snippet or self._marker_snippet,
        }
        vals.update(overrides)
        return self.conf_model.create(vals)

    def test_notify_done_triggers_global_conf(self):
        conf = self._make_conf(self.trigger_done, "Global Done")
        self.record._notify_done()
        self.assertEqual(conf.description, f"|{self.record._name}")

    def test_notify_error_triggers_global_conf(self):
        conf = self._make_conf(self.trigger_error, "Global Error")
        self.record._notify_error("send_ko")
        self.assertEqual(conf.description, f"|{self.record._name}")

    def test_notify_ack_received_triggers_global_conf(self):
        conf = self._make_conf(self.trigger_ack_received, "Global ACK received")
        self.record._notify_ack_received()
        self.assertEqual(conf.description, f"|{self.record._name}")

    def test_notify_ack_missing_triggers_global_conf(self):
        conf = self._make_conf(self.trigger_ack_missing, "Global ACK missing")
        self.record._notify_ack_missing()
        self.assertEqual(conf.description, f"|{self.record._name}")

    def test_notify_ack_received_error_triggers_global_conf(self):
        conf = self._make_conf(
            self.trigger_ack_received_error, "Global ACK received error"
        )
        self.record._notify_ack_received_error()
        self.assertEqual(conf.description, f"|{self.record._name}")

    def test_non_global_conf_is_ignored(self):
        conf = self._make_conf(self.trigger_done, "Non Global Done", is_global=False)
        self.record._notify_done()
        self.assertFalse(conf.description)

    def test_inactive_global_conf_is_ignored(self):
        conf = self._make_conf(self.trigger_done, "Inactive Global Done")
        conf.active = False
        self.record._notify_done()
        self.assertFalse(conf.description)

    def test_notify_action_complete_dispatches_to_both_targets(self):
        """`notify_action_complete` fires the event twice when the related
        record exists: once with the exchange record as target, once with the
        related record (partner here)."""
        conf = self._make_conf(
            self.trigger_generate_complete, "Global generate complete"
        )
        # Sanity check: the exchange record has a related record.
        self.assertTrue(self.record.related_record_exists)
        self.record.notify_action_complete("generate")
        # The snippet appended one marker per call: exchange record then partner.
        self.assertEqual(
            conf.description,
            f"|{self.record._name}|{self.partner._name}",
        )

    def test_notify_action_complete_no_related_record(self):
        """When no related record exists, the event fires only on the
        exchange record itself."""
        conf = self._make_conf(
            self.trigger_generate_complete, "Global generate complete - no related"
        )
        # Create an exchange record with no related record.
        orphan_record = self.backend.create_record(
            "test_csv_output", {"model": False, "res_id": False}
        )
        orphan_record.notify_action_complete("generate")
        self.assertEqual(conf.description, f"|{orphan_record._name}")

    def test_snippet_receives_conf_and_record(self):
        """The snippet eval context must expose both `conf` (the configuration)
        and `record` (the target of the event)."""
        snippet = (
            "conf.write({'description': 'conf=%s|record=%s' % "
            "(conf.name, record.display_name)})"
        )
        conf = self._make_conf(self.trigger_done, "Context check", snippet=snippet)
        self.record._notify_done()
        self.assertEqual(
            conf.description,
            f"conf={conf.name}|record={self.record.display_name}",
        )

    def test_multiple_global_confs_all_executed(self):
        """All global confs matching the trigger are executed."""
        conf1 = self._make_conf(self.trigger_done, "Global Done 1")
        conf2 = self._make_conf(self.trigger_done, "Global Done 2")
        self.record._notify_done()
        self.assertEqual(conf1.description, f"|{self.record._name}")
        self.assertEqual(conf2.description, f"|{self.record._name}")

    # ------------------------------------------------------------------
    # Filtering tests for `edi_get_conf_global`
    # ------------------------------------------------------------------
    def test_filter_by_type_mismatch(self):
        """A conf bound to a different exchange type must not fire."""
        conf = self._make_conf(
            self.trigger_done,
            "Wrong type",
            type_id=self.exchange_type_in.id,
        )
        self.record._notify_done()
        self.assertFalse(conf.description)

    def test_filter_by_type_empty_matches(self):
        """A conf without a type matches any exchange record's type."""
        conf = self._make_conf(self.trigger_done, "No type", type_id=False)
        self.record._notify_done()
        self.assertEqual(conf.description, f"|{self.record._name}")

    def test_filter_by_backend_mismatch(self):
        """A conf bound to a different backend must not fire."""
        other_backend = self.env["edi.backend"].create(
            {
                "name": "Other backend",
                "backend_type_id": self.backend.backend_type_id.id,
            }
        )
        # `_constrains_backend` requires backend to be compatible with the type's
        # backend if the type has one set. Detach the type from the conf to test
        # only the backend filter.
        conf = self._make_conf(
            self.trigger_done,
            "Wrong backend",
            backend_id=other_backend.id,
            type_id=False,
        )
        self.record._notify_done()
        self.assertFalse(conf.description)

    def test_filter_by_backend_empty_matches(self):
        """A conf without a backend matches any exchange record's backend."""
        conf = self._make_conf(
            self.trigger_done,
            "No backend",
            backend_id=False,
            type_id=False,
        )
        self.record._notify_done()
        self.assertEqual(conf.description, f"|{self.record._name}")

    def test_filter_by_model_mismatch(self):
        """A conf bound to a different model must not fire."""
        other_model = self.env["ir.model"]._get("res.users")
        conf = self._make_conf(
            self.trigger_done,
            "Wrong model",
            model_id=other_model.id,
        )
        self.record._notify_done()
        self.assertFalse(conf.description)

    def test_filter_by_model_match(self):
        """A conf bound to the related record model fires."""
        partner_model = self.env["ir.model"]._get(self.partner._name)
        conf = self._make_conf(
            self.trigger_done,
            "Matching model",
            model_id=partner_model.id,
        )
        self.record._notify_done()
        self.assertEqual(conf.description, f"|{self.record._name}")

    def test_filter_by_model_orphan_record(self):
        """A conf with a model is skipped on records with no related model."""
        partner_model = self.env["ir.model"]._get(self.partner._name)
        conf_with_model = self._make_conf(
            self.trigger_done,
            "Model bound",
            model_id=partner_model.id,
        )
        conf_no_model = self._make_conf(self.trigger_done, "Model-less")
        orphan_record = self.backend.create_record(
            "test_csv_output", {"model": False, "res_id": False}
        )
        orphan_record._notify_done()
        self.assertFalse(conf_with_model.description)
        self.assertEqual(conf_no_model.description, f"|{orphan_record._name}")

    def test_edi_get_conf_global_returns_only_matching(self):
        """Direct check on the new helper method."""
        matching = self._make_conf(self.trigger_done, "Matching")
        wrong_trigger = self._make_conf(self.trigger_error, "Wrong trigger")
        non_global = self._make_conf(self.trigger_done, "Non global", is_global=False)
        result = self.env["edi.configuration"].edi_get_conf_global(
            self.record, self.trigger_done.code
        )
        self.assertIn(matching, result)
        self.assertNotIn(wrong_trigger, result)
        self.assertNotIn(non_global, result)
