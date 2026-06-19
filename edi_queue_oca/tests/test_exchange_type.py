# Copyright 2026 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime

from freezegun import freeze_time

from .common import EDIQueueCommonTestCase


class EDIExchangeTypeTestCase(EDIQueueCommonTestCase):
    def setUp(self):
        super().setUp()
        self.record = self._make_record()

    def _get_job_eta(self, record):
        return self._get_delayed(record).delayable.eta

    def test_job_eta_disabled_no_eta_applied(self):
        """job_eta_enabled=False: no ETA is set regardless of value."""
        self.exchange_type_in.job_eta_hour = "22"
        self.exchange_type_in.job_eta_minute = "00"
        # job_eta_enabled defaults to False
        self.assertIsNone(self._get_job_eta(self.record))

    @freeze_time("2024-01-15 20:00:00")
    def test_job_eta_scheduled_same_day(self):
        """ETA not yet reached today: job lands on the same calendar day."""
        self.env.user.tz = "UTC"
        self.exchange_type_in.job_eta_enabled = True
        self.exchange_type_in.job_eta_hour = "22"
        self.exchange_type_in.job_eta_minute = "00"
        self.assertEqual(
            self._get_job_eta(self.record),
            datetime(2024, 1, 15, 22, 0, 0),
        )

    @freeze_time("2024-01-15 23:00:00")
    def test_job_eta_scheduled_next_day(self):
        """ETA already passed today: job rolls over to the next calendar day."""
        self.env.user.tz = "UTC"
        self.exchange_type_in.job_eta_enabled = True
        self.exchange_type_in.job_eta_hour = "22"
        self.exchange_type_in.job_eta_minute = "00"
        self.assertEqual(
            self._get_job_eta(self.record),
            datetime(2024, 1, 16, 22, 0, 0),
        )

    @freeze_time("2024-01-15 20:00:00")
    def test_job_eta_midnight_schedules_next_day(self):
        """Midnight (00:00) schedules for the next 00:00 in user TZ."""
        self.env.user.tz = "UTC"
        self.exchange_type_in.job_eta_enabled = True
        self.exchange_type_in.job_eta_hour = "00"
        self.exchange_type_in.job_eta_minute = "00"
        self.assertEqual(
            self._get_job_eta(record=self.record),
            datetime(2024, 1, 16, 0, 0, 0),
        )
