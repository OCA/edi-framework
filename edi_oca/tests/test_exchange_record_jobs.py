# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

from requests.exceptions import ConnectionError as ReqConnectionError

from odoo.addons.queue_job.exception import RetryableJobError
from odoo.addons.queue_job.tests.common import JobMixin

from .common import EDIBackendCommonTestCase


class EDIExchangeRecordTestJobsCase(EDIBackendCommonTestCase, JobMixin):
    @classmethod
    def _setup_context(cls):
        return dict(super()._setup_context(), test_queue_job_no_delay=None)

    def test_output(self):
        job_counter = self.job_counter()
        vals = {
            "model": self.partner._name,
            "res_id": self.partner.id,
        }
        record = self.backend.create_record("test_csv_output", vals)
        self.assertEqual(record.edi_exchange_state, "new")
        job = record.with_delay().action_exchange_generate()
        created = job_counter.search_created()
        self.assertEqual(len(created), 1)
        self.assertEqual(created.name, "edi.exchange.record.action_exchange_generate")
        with mock.patch.object(
            type(self.backend), "_exchange_generate"
        ) as mocked_generate, mock.patch.object(
            type(self.backend), "_validate_data"
        ) as mocked_validate:
            mocked_generate.return_value = "filecontent"
            mocked_validate.return_value = None
            res = job.perform()
            self.assertEqual(res, "Exchange data generated")
            self.assertEqual(record.edi_exchange_state, "output_pending")
        job = record.with_delay().action_exchange_send()
        created = job_counter.search_created()
        with mock.patch.object(type(self.backend), "_exchange_send") as mocked:
            mocked.return_value = "ok"
            res = job.perform()
            self.assertEqual(res, "Exchange sent")
            self.assertEqual(record.edi_exchange_state, "output_sent")
        self.assertEqual(created[0].name, "edi.exchange.record.action_exchange_send")

    def test_output_fail_retry(self):
        job_counter = self.job_counter()
        vals = {
            "model": self.partner._name,
            "res_id": self.partner.id,
            "edi_exchange_state": "output_pending",
        }
        record = self.backend.create_record("test_csv_output", vals)
        record._set_file_content("ABC")
        job = record.with_delay().action_exchange_send()
        job_counter.search_created()
        with mock.patch.object(type(self.backend), "_exchange_send") as mocked:
            mocked.side_effect = ReqConnectionError("Connection broken")
            with self.assertRaises(RetryableJobError):
                job.perform()

    def test_input(self):
        job_counter = self.job_counter()
        vals = {
            "model": self.partner._name,
            "res_id": self.partner.id,
        }
        record = self.backend.create_record("test_csv_input", vals)
        job = record.with_delay().action_exchange_receive()
        created = job_counter.search_created()
        self.assertEqual(len(created), 1)
        self.assertEqual(created.name, "edi.exchange.record.action_exchange_receive")
        with mock.patch.object(
            type(self.backend), "_exchange_receive"
        ) as mocked_receive, mock.patch.object(
            type(self.backend), "_validate_data"
        ) as mocked_validate:
            mocked_receive.return_value = "filecontent"
            mocked_validate.return_value = None
            res = job.perform()
            # the state is not input_pending hence there's nothing to do
            self.assertEqual(res, "Nothing to do. Likely already received.")
            record.edi_exchange_state = "input_pending"
            res = job.perform()
            # the state is not input_pending hence there's nothing to do
            self.assertEqual(res, "Exchange received successfully")
            self.assertEqual(record.edi_exchange_state, "input_received")
        job = record.with_delay().action_exchange_process()
        created = job_counter.search_created()
        self.assertEqual(created[0].name, "edi.exchange.record.action_exchange_process")

    def test_input_processed_error(self):
        vals = {
            "model": self.partner._name,
            "res_id": self.partner.id,
            "edi_exchange_state": "input_received",
        }
        record = self.backend.create_record("test_csv_input", vals)
        record._set_file_content("ABC")
        # Process `input_received` records
        job_counter = self.job_counter()
        self.backend._check_input_exchange_sync()
        created = job_counter.search_created()
        # Create job
        self.assertEqual(len(created), 1)
        record.edi_exchange_state = "input_processed_error"
        # Don't re-process `input_processed_error` records
        self.backend._check_input_exchange_sync()
        new_created = job_counter.search_created() - created
        # Should not create new job
        self.assertEqual(len(new_created), 0)
