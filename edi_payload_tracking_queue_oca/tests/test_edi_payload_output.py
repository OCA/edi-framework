# Copyright 2026 Camptocamp SA
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from unittest.mock import patch

from odoo.tests import tagged

from odoo.addons.edi_payload_tracking_oca.tests.common import PayloadTrackingTestCase
from odoo.addons.queue_job.exception import RetryableJobError


@tagged("post_install", "-at_install")
class TestEDIPayloadOutputQueue(PayloadTrackingTestCase):
    """Retry the job storing a payload created concurrently."""

    def test_set_payload_created_concurrently_is_retried(self):
        """A payload created by a concurrent job makes the job retry."""
        self.payload_model.set_payload(self.record, {"name": "first"})
        # A payload committed by a concurrent job after this transaction
        # started is not visible to it: the lookup misses it and the insert
        # collides with it.
        with (
            patch.object(
                type(self.payload_model),
                "_find_for_record",
                return_value=self.payload_model.browse(),
            ),
            self.assertRaises(RetryableJobError),
        ):
            self.payload_model.set_payload(self.record, {"name": "second"})
        self.assertEqual(self.record.edi_payload_get_output(), {"name": "first"})
