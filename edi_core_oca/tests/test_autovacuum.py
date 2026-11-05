# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tools import SQL, mute_logger

from .common import EDIBackendCommonTestCase


class EDIRecordAutovacuumTestCase(EDIBackendCommonTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        vals = {"model": cls.partner._name, "res_id": cls.partner.id}
        cls.old_record = cls.backend.create_record("test_csv_output", vals)
        cls.recent_record = cls.backend.create_record("test_csv_output", vals)
        cls._set_age(cls.old_record, days=40)
        cls._set_age(cls.recent_record, days=5)

    @classmethod
    def _set_age(cls, record, days):
        record.flush_recordset()
        cls.env.cr.execute(
            SQL(
                "UPDATE edi_exchange_record "
                "SET create_date = (now() AT TIME ZONE 'UTC') - %s * interval '1 day' "
                "WHERE id = %s",
                days,
                record.id,
            )
        )
        record.invalidate_recordset(["create_date"])

    def _run_autovacuum(self):
        with self.enter_registry_test_mode(), mute_logger("odoo.models.unlink"):
            self.env.ref("base.autovacuum_job").method_direct_trigger()

    def test_archive_old_records(self):
        """Records older than the backend's setting get archived.

        Scenario:
            1. Set the backend to archive its records after 30 days.
            2. Run the autovacuum.
        Expected:
            - The record created 40 days ago is archived.
            - The record created 5 days ago stays active.
        """
        self.backend.auto_archive_records_after_days = 30
        self._run_autovacuum()
        self.assertFalse(self.old_record.active)
        self.assertTrue(self.recent_record.active)

    def test_archive_disabled(self):
        """Nothing is archived when the backend does not ask for it."""
        self.backend.auto_archive_records_after_days = 0
        self._run_autovacuum()
        self.assertTrue(self.old_record.active)

    def test_delete_old_archived_records(self):
        """Archived records older than the backend's setting get deleted.

        Scenario:
            1. Set the backend to delete its archived records after 30 days.
            2. Archive both records, and run the autovacuum.
        Expected:
            - The record created 40 days ago is deleted.
            - The record created 5 days ago is kept.
        """
        self.backend.auto_delete_records_after_days = 30
        (self.old_record | self.recent_record).action_archive()
        self._run_autovacuum()
        self.assertFalse(self.old_record.exists())
        self.assertTrue(self.recent_record.exists())

    def test_delete_keeps_active_records(self):
        """Old records still active are not deleted."""
        self.backend.auto_delete_records_after_days = 30
        self._run_autovacuum()
        self.assertTrue(self.old_record.exists())

    def test_batch_result(self):
        """The cleanup reports what it did, and whether records remain.

        The base autovacuum cron calls it again while records remain.
        """
        self.backend.auto_archive_records_after_days = 30
        done, remaining = self.env["edi.exchange.record"]._gc_archive_old_records()
        self.assertGreaterEqual(done, 1)
        self.assertFalse(remaining)
