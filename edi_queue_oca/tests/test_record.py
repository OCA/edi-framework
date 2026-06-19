# Copyright 2020 ACSONE
# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime

import pytz

from odoo.addons.queue_job.delay import DelayableRecordset

from .common import EDIQueueCommonTestCase


class EDIRecordTestCase(EDIQueueCommonTestCase):
    def test_with_delay_override(self):
        record = self._make_record()
        parent_channel = self.env["queue.job.channel"].create(
            {
                "name": "parent_test_chan",
                "parent_id": self.env.ref("queue_job.channel_root").id,
            }
        )
        channel = self.env["queue.job.channel"].create(
            {"name": "test_chan", "parent_id": parent_channel.id}
        )
        self.exchange_type_in.job_channel_id = channel
        self.exchange_type_in.job_priority = 5
        # re-enable job delayed feature
        delayed = self._get_delayed(record)
        self.assertTrue(isinstance(delayed, DelayableRecordset))
        self.assertEqual(delayed.recordset, record)
        self.assertEqual(delayed.delayable.channel, "root.parent_test_chan.test_chan")
        self.assertEqual(delayed.delayable.priority, 5)

    def test_with_delay_job_eta_applied(self):
        record = self._make_record()
        parent_channel = self.env["queue.job.channel"].create(
            {
                "name": "parent_test_chan",
                "parent_id": self.env.ref("queue_job.channel_root").id,
            }
        )
        channel = self.env["queue.job.channel"].create(
            {"name": "test_chan", "parent_id": parent_channel.id}
        )
        self.exchange_type_in.job_channel_id = channel
        self.exchange_type_in.job_priority = 5
        self.exchange_type_in.job_eta_enabled = True
        self.exchange_type_in.job_eta_hour = "22"
        self.exchange_type_in.job_eta_minute = "00"
        delayed = self._get_delayed(record)
        job_eta = delayed.delayable.eta
        utc_tz = pytz.UTC
        user_tz = pytz.timezone(self.env.user.tz or "UTC")
        target_22h_user = datetime.now(user_tz).replace(
            hour=22, minute=0, second=0, microsecond=0
        )
        expected_eta = target_22h_user.astimezone(utc_tz).replace(tzinfo=None)
        self.assertTrue(isinstance(delayed, DelayableRecordset))
        self.assertEqual(delayed.recordset, record)
        self.assertEqual(job_eta, expected_eta)
        self.assertEqual(delayed.delayable.channel, "root.parent_test_chan.test_chan")
        self.assertEqual(delayed.delayable.priority, 5)
