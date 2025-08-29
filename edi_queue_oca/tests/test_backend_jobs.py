# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from unittest import mock

from odoo_test_helper import FakeModelLoader
from requests.exceptions import ConnectionError as ReqConnectionError

from odoo.tests import tagged

from odoo.addons.edi_core_oca.tests.common import EDIBackendCommonTestCase
from odoo.addons.queue_job.exception import RetryableJobError
from odoo.addons.queue_job.tests.common import JobMixin


@tagged("-at_install", "post_install")
class EDIBackendTestJobsCase(EDIBackendCommonTestCase, JobMixin):
    @classmethod
    def _setup_context(cls):
        return dict(super()._setup_context(), queue_job__no_delay=None)

    @classmethod
    def _setup_records(cls):  # pylint:disable=missing-return
        super()._setup_records()
        # Load fake models ->/
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from odoo.addons.edi_core_oca.tests.fake_models import EdiTestExecution

        cls.loader.update_registry((EdiTestExecution,))
        cls.ExecutionAbstractModel = cls.env["edi.framework.test.execution"]
        cls.model = cls.env["ir.model"].search(
            [("model", "=", "edi.framework.test.execution")]
        )
        cls.exchange_type_out.generate_model_id = cls.model
        cls.exchange_type_out.send_model_id = cls.model
        cls.exchange_type_out.output_validate_model_id = cls.model
        cls.exchange_type_in.receive_model_id = cls.model
        cls.exchange_type_in.process_model_id = cls.model
        cls.exchange_type_in.input_validate_model_id = cls.model

    def _get_related_jobs(self, record):
        # Use domain in action to find all related jobs
        record.ensure_one()
        action = record.action_view_related_queue_jobs()
        return self.env["queue.job"].search(action["domain"])

    def test_output(self):
        job_counter = self.job_counter()
        vals = {
            "model": self.partner._name,
            "res_id": self.partner.id,
        }
        record = self.backend.create_record("test_csv_output", vals)
        self.assertEqual(record.edi_exchange_state, "new")
        job = self.backend.with_delay().exchange_generate(record)
        created = job_counter.search_created()
        self.assertEqual(len(created), 1)
        self.assertEqual(
            created.name, "Generate output content for given exchange record."
        )
        # Check related jobs
        self.assertEqual(created, self._get_related_jobs(record))
        with (
            mock.patch.object(
                type(self.backend), "_exchange_generate"
            ) as mocked_generate,
            mock.patch.object(type(self.backend), "_validate_data") as mocked_validate,
        ):
            mocked_generate.return_value = "filecontent"
            mocked_validate.return_value = None
            res = job.perform()
            self.assertEqual(res, "Exchange data generated")
            self.assertEqual(record.edi_exchange_state, "output_pending")
        job = self.backend.with_delay().exchange_send(record)
        created = job_counter.search_created()
        with mock.patch.object(type(self.backend), "_exchange_send") as mocked:
            mocked.return_value = "ok"
            res = job.perform()
            self.assertEqual(res, "Exchange sent")
            self.assertEqual(record.edi_exchange_state, "output_sent")
        self.assertEqual(created[0].name, "Send exchange file.")
        # Check related jobs
        record.invalidate_recordset()
        self.assertEqual(created, self._get_related_jobs(record))

    def test_output_fail_retry(self):
        job_counter = self.job_counter()
        vals = {
            "model": self.partner._name,
            "res_id": self.partner.id,
            "edi_exchange_state": "output_pending",
        }
        record = self.backend.create_record("test_csv_output", vals)
        record._set_file_content("ABC")
        job = self.backend.with_delay().exchange_send(record)
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
        job = self.backend.with_delay().exchange_receive(record)
        created = job_counter.search_created()
        self.assertEqual(len(created), 1)
        self.assertEqual(created.name, "Retrieve an incoming document.")
        # Check related jobs
        self.assertEqual(created, self._get_related_jobs(record))
        with (
            mock.patch.object(
                type(self.backend), "_exchange_receive"
            ) as mocked_receive,
            mock.patch.object(type(self.backend), "_validate_data") as mocked_validate,
        ):
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
        job = self.backend.with_delay().exchange_process(record)
        created = job_counter.search_created()
        self.assertEqual(created[0].name, "Process an incoming document.")

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
        # Check related jobs
        record.invalidate_recordset()
        self.assertEqual(created, self._get_related_jobs(record))
