# Copyright 2020 ACSONE
# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo.addons.edi_core_oca.tests.common import EDIBackendCommonTestCase
from odoo.addons.queue_job.delay import DelayableRecordset


class EDIRecordTestCase(EDIBackendCommonTestCase):
    def test_with_delay_override(self):
        vals = {
            "model": self.partner._name,
            "res_id": self.partner.id,
        }
        record = self.backend.create_record("test_csv_input", vals)
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
        delayed = record.with_context(queue_job__no_delay=False).with_delay()
        # Silent useless warning
        # `Delayable Delayable(edi.exchange.record*) was prepared but never delayed`
        delayed.delayable._generated_job = object()
        self.assertTrue(isinstance(delayed, DelayableRecordset))
        self.assertEqual(delayed.recordset, record)
        self.assertEqual(delayed.delayable.channel, "root.parent_test_chan.test_chan")
        self.assertEqual(delayed.delayable.priority, 5)
