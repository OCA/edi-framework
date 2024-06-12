# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.queue_job.tests.common import JobMixin

from .common import EDIBackendCommonTestCase


class EDIBackendTestJobsCase(EDIBackendCommonTestCase, JobMixin):
    @classmethod
    def _setup_context(cls):
        return dict(super()._setup_context(), queue_job__no_delay=None)

    def test_output(self):
        job_counter = self.job_counter()
        vals = {
            "model": self.partner._name,
            "res_id": self.partner.id,
        }
        record = self.backend.create_record("test_csv_output", vals)
        self.backend.with_delay().exchange_generate(record)
        created = job_counter.search_created()
        self.assertEqual(len(created), 1)
        self.assertEqual(
            created.name, "Generate output content for given exchange record."
        )
        self.backend.with_delay().exchange_send(record)
        created = job_counter.search_created()
        self.assertEqual(created[0].name, "Send exchange file.")

    def test_input(self):
        job_counter = self.job_counter()
        vals = {
            "model": self.partner._name,
            "res_id": self.partner.id,
        }
        record = self.backend.create_record("test_csv_input", vals)
        self.backend.with_delay().exchange_receive(record)
        created = job_counter.search_created()
        self.assertEqual(len(created), 1)
        self.assertEqual(created.name, "Retrieve an incoming document.")
        self.backend.with_delay().exchange_process(record)
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
