# Copyright 2020 ACSONE
# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from freezegun import freeze_time

from odoo.tools import mute_logger

from .common import EDIBackendCommonTestCase


class EDIExchangeTypeTestCase(EDIBackendCommonTestCase):
    def test_copy(self):
        new_type = self.exchange_type_out.copy()
        self.assertEqual(new_type.code, f"{self.exchange_type_out.code}_COPY_FIXME")
        self.assertEqual(
            new_type.backend_type_id, self.exchange_type_out.backend_type_id
        )
        self.assertEqual(new_type.backend_id, self.exchange_type_out.backend_id)

    def test_ack_for(self):
        self.assertEqual(self.exchange_type_out.ack_type_id, self.exchange_type_out_ack)
        new_type = self.exchange_type_out.copy({"code": "just_a_test"})
        self.assertEqual(new_type.ack_type_id, self.exchange_type_out_ack)
        self.exchange_type_out_ack.invalidate_recordset()
        self.assertIn(
            self.exchange_type_out.id,
            self.exchange_type_out_ack.ack_for_type_ids.ids,
        )
        self.assertIn(
            new_type.id,
            self.exchange_type_out_ack.ack_for_type_ids.ids,
        )

    @mute_logger("odoo.sql_db")
    def test_same_code_same_backend(self):
        with mute_logger("odoo.sql_db"):
            with self.assertRaises(Exception) as err:
                self.exchange_type_in.copy({"code": "test_csv_input"})
        err_msg = err.exception.args[0]
        self.assertTrue(
            err_msg.startswith("duplicate key value violates unique constraint")
        )

    def test_same_code_different_backend(self):
        new_backend = self.backend.copy()
        new_type = self.exchange_type_in.copy(
            {"backend_id": new_backend.id, "code": "test_csv_input"}
        )
        self.assertEqual(new_type.code, self.exchange_type_in.code)
        self.assertEqual(
            new_type.backend_type_id, self.exchange_type_in.backend_type_id
        )
        self.assertNotEqual(new_type.backend_id, self.exchange_type_in.backend_id)

    def test_advanced_settings(self):
        settings = """
        components:
            foo: this
            boo: that
        whatever:
            ok: True
        """
        self.exchange_type_out.advanced_settings_edit = settings
        # fmt:off
        self.assertEqual(self.exchange_type_out.advanced_settings, {
            "components": {
                "foo": "this",
                "boo": "that",
            },
            "whatever": {
                "ok": True,
            }
        })
        # fmt:on

    def _test_exchange_filename(self, wanted_filename):
        filename = self.exchange_type_out._make_exchange_filename(
            exchange_record=self.env["edi.exchange.record"]
        )
        self.assertEqual(filename, wanted_filename)

    @freeze_time("2022-04-28 08:37:24")
    def test_filename_pattern_settings(self):
        """
        Test filename pattern defined into advanced settings.

        Example of pattern:
          filename_pattern:
            force_tz: Europe/Rome
            date_pattern: %Y-%m-%d-%H-%M-%S
        """

        self.env.user.tz = None
        self.exchange_type_out.write(
            {
                "exchange_filename_pattern": "Test-File",
                "exchange_file_ext": "csv",
                "advanced_settings_edit": None,
            }
        )

        # Test without any settings and minimal filename pattern
        self._test_exchange_filename("Test-File.csv")

        # Test without extension for filename pattern
        self.exchange_type_out.exchange_file_ext = False
        self._test_exchange_filename("Test-File")

        # Test with datetime in filename pattern
        self.exchange_type_out.exchange_file_ext = "csv"
        self.exchange_type_out.exchange_filename_pattern = "Test-File-{dt}"
        self._test_exchange_filename("Test-File-2022-04-28-08-37-24.csv")

        # Add timezone on current user
        self.env.user.tz = "America/New_York"  # New_York time is -4h
        self._test_exchange_filename("Test-File-2022-04-28-04-37-24.csv")

        # Force date pattern on advanced settings
        self.exchange_type_out.advanced_settings_edit = """
        filename_pattern:
            date_pattern: '%Y-%m-%d-%H'
        """
        self._test_exchange_filename("Test-File-2022-04-28-04.csv")

        # Force timezone on advanced settings
        self.exchange_type_out.advanced_settings_edit = """
        filename_pattern:
            # Rome time is +2h
            force_tz: Europe/Rome
        """
        self._test_exchange_filename("Test-File-2022-04-28-10-37-24.csv")

        # Force date pattern and timezone on advanced settings
        self.exchange_type_out.advanced_settings_edit = """
        filename_pattern:
            # Rome time is +2h
            force_tz: Europe/Rome
            date_pattern: '%Y-%m-%d-%H-%M'
        """
        self._test_exchange_filename("Test-File-2022-04-28-10-37.csv")

        # Test with sequence in filename pattern
        self.exchange_type_out.exchange_filename_pattern = "Test-File-{seq}"
        self.exchange_type_out.exchange_filename_sequence_id = self.sequence
        self._test_exchange_filename("Test-File-0000001.csv")

    def test_archive_rules(self):
        exc_type = self.exchange_type_out
        rule1 = exc_type.rule_ids.create(
            {
                "type_id": exc_type.id,
                "name": "Fake partner rule",
                "model_id": self.env["ir.model"]._get("res.partner").id,
            }
        )
        rule2 = exc_type.rule_ids.create(
            {
                "type_id": exc_type.id,
                "name": "Fake user rule",
                "model_id": self.env["ir.model"]._get("res.users").id,
            }
        )
        exc_type.active = False
        rule1.invalidate_recordset()
        rule2.invalidate_recordset()
        self.assertFalse(rule1.active)
        self.assertFalse(rule2.active)

    def _create_exchange_record(self, exc_type):
        return self.backend.create_record(
            exc_type.code,
            {"model": self.partner._name, "res_id": self.partner.id},
        )

    def test_exchange_record_count(self):
        exc_type = self.exchange_type_out
        self.assertEqual(exc_type.exchange_record_count, 0)
        rec1 = self._create_exchange_record(exc_type)
        rec2 = self._create_exchange_record(exc_type)
        # Record on a different type must not be counted
        self._create_exchange_record(self.exchange_type_in)
        self.assertEqual(exc_type.exchange_record_count, 2)
        self.assertEqual(set(exc_type.exchange_record_ids.ids), {rec1.id, rec2.id})

    def test_action_view_exchange_records(self):
        exc_type = self.exchange_type_out
        rec = self._create_exchange_record(exc_type)
        action = exc_type.action_view_exchange_records()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "edi.exchange.record")
        self.assertIn(("type_id", "=", exc_type.id), action["domain"])
        ctx = action["context"]
        self.assertEqual(ctx.get("default_type_id"), exc_type.id)
        self.assertEqual(ctx.get("default_backend_id"), exc_type.backend_id.id)
        self.assertEqual(ctx.get("search_default_type_id"), exc_type.id)
        # The action's domain must actually match the created exchange record
        records = self.env[action["res_model"]].search(action["domain"])
        self.assertIn(rec, records)

    def test_action_view_exchange_records_requires_singleton(self):
        with self.assertRaises(ValueError):
            (
                self.exchange_type_out | self.exchange_type_in
            ).action_view_exchange_records()
