# Copyright 2026 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from unittest import mock

from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.queue_job.tests.common import JobMixin

from .common import EDIQueueCommonTestCase

ALLOWED = (
    "{identifier}, {external_identifier}, {type}, {type_code}, {backend}, {record}"
)


@tagged("-at_install", "post_install")
class EDIJobDescriptionTestCase(EDIQueueCommonTestCase, JobMixin):
    """Job description built from the exchange type pattern."""

    def setUp(self):
        super().setUp()
        self.record_in = self._make_record()
        self.record_out = self.backend.create_record(
            "test_csv_output",
            {"model": self.partner._name, "res_id": self.partner.id},
        )

    def _delay(self, record):
        return record.with_context(queue_job__no_delay=False)

    def _calls_info(self, trap):
        return [
            (
                call.method.__name__,
                call.properties.get("description"),
                call.properties.get("priority"),
            )
            for call in trap.calls
        ]

    def test_actions_job_description(self):
        """Every auto-delayed action gets the description, send keeps priority 0."""
        self.exchange_type_in.job_description_pattern = "In {identifier}"
        self.exchange_type_out.job_description_pattern = "Out {identifier}"
        with self.trap_jobs() as trap:
            self._delay(self.record_out).action_exchange_generate()
            self._delay(self.record_out).action_exchange_send()
            self._delay(self.record_in).action_exchange_receive()
            self._delay(self.record_in).action_exchange_process()
        out_desc = f"Out {self.record_out.identifier}"
        in_desc = f"In {self.record_in.identifier}"
        self.assertEqual(
            self._calls_info(trap),
            [
                ("action_exchange_generate", out_desc, None),
                ("action_exchange_send", out_desc, 0),
                ("action_exchange_receive", in_desc, None),
                ("action_exchange_process", in_desc, None),
            ],
        )

    def test_chained_jobs_description(self):
        """Chained jobs created by the backend crons get the description too."""
        self.exchange_type_in.job_description_pattern = "In {identifier}"
        self.exchange_type_out.job_description_pattern = "Out {identifier}"
        with self.trap_jobs() as trap:
            self._delay(self.record_out).action_exchange_generate_send_chained()
            self._delay(self.record_in).action_exchange_receive_process_chained()
        out_desc = f"Out {self.record_out.identifier}"
        in_desc = f"In {self.record_in.identifier}"
        # The order of the jobs of a graph is not relevant
        self.assertCountEqual(
            self._calls_info(trap),
            [
                ("action_exchange_generate", out_desc, None),
                ("action_exchange_send", out_desc, 0),
                ("action_exchange_receive", in_desc, None),
                ("action_exchange_process", in_desc, 0),
            ],
        )

    def test_no_pattern_no_description(self):
        """Without pattern, no description is passed to the jobs."""
        self.assertIsNone(self.record_in._job_description_get())
        with self.trap_jobs() as trap:
            self._delay(self.record_out).action_exchange_send()
            self._delay(self.record_in).action_exchange_process()
        self.assertEqual(
            self._calls_info(trap),
            [
                ("action_exchange_send", None, 0),
                ("action_exchange_process", None, None),
            ],
        )

    def test_job_options_description_wins(self):
        """A description returned by a job options override wins over the pattern."""
        self.exchange_type_in.job_description_pattern = "In {identifier}"
        with (
            mock.patch.object(
                type(self.record_in),
                "action_exchange_process_job_options",
                create=True,
                return_value={"description": "Custom"},
            ),
            self.trap_jobs() as trap,
        ):
            self._delay(self.record_in).action_exchange_process()
        self.assertEqual(
            self._calls_info(trap), [("action_exchange_process", "Custom", None)]
        )

    def test_placeholders(self):
        """All placeholders are rendered from the exchange record."""
        self.exchange_type_in.job_description_pattern = (
            "{identifier}|{external_identifier}|{type}|{type_code}|{backend}|{record}"
        )
        self.record_in.external_identifier = "EXT-1"
        self.assertEqual(
            self.record_in._job_description_get(),
            f"{self.record_in.identifier}|EXT-1|Test CSV input|test_csv_input"
            "|Demo backend|EDI EXC TEST",
        )

    def test_placeholders_missing_values(self):
        """Missing values are rendered as empty strings."""
        self.exchange_type_in.job_description_pattern = (
            "{identifier}|{external_identifier}|{record}"
        )
        record = self.backend.create_record("test_csv_input", {})
        self.assertEqual(record._job_description_get(), f"{record.identifier}||")

    def test_several_records_no_description(self):
        """No description is computed for several records at once."""
        self.exchange_type_in.job_description_pattern = "In {identifier}"
        records = self.record_in | self._make_record()
        self.assertIsNone(records._job_description_get())

    def test_invalid_patterns(self):
        """Patterns with unsafe or unknown fields are rejected on save."""
        cases = {
            "{identifier.__class__}": "unsupported placeholder {identifier.__class__}",
            "{identifier[0]}": "unsupported placeholder {identifier[0]}",
            "Exchange {}": "unsupported placeholder {}",
            "Exchange {0}": "unsupported placeholder {0}",
            "{foo}": "unsupported placeholder {foo}",
            "{identifier:{type.__class__}}": (
                "unsupported placeholder {type.__class__}"
            ),
            "{identifier:d}": "Unknown format code 'd' for object of type 'str'",
            "{identifier": "expected '}' before end of string",
        }
        for pattern, error in cases.items():
            with (
                self.subTest(pattern=pattern),
                self.assertRaises(ValidationError) as cm,
            ):
                self.exchange_type_in.job_description_pattern = pattern
            self.assertEqual(
                str(cm.exception),
                f'Invalid job description pattern "{pattern}": {error}. '
                f"Allowed placeholders: {ALLOWED}.",
            )

    def test_runtime_fallback(self):
        """An invalid pattern stored anyway logs a warning and gives no description."""
        self.env.cr.execute(
            "UPDATE edi_exchange_type SET job_description_pattern = %s WHERE id = %s",
            ("{identifier.__class__}", self.exchange_type_in.id),
        )
        self.exchange_type_in.invalidate_recordset(["job_description_pattern"])
        with (
            self.assertLogs(
                "odoo.addons.edi_queue_oca.models.edi_exchange_record", "WARNING"
            ) as logs,
            self.trap_jobs() as trap,
        ):
            self._delay(self.record_in).action_exchange_process()
        self.assertEqual(
            logs.output,
            [
                "WARNING:odoo.addons.edi_queue_oca.models.edi_exchange_record:"
                "Cannot render job description pattern '{identifier.__class__}' "
                "of exchange type test_csv_input: "
                "unsupported placeholder {identifier.__class__}"
            ],
        )
        self.assertEqual(
            self._calls_info(trap), [("action_exchange_process", None, None)]
        )
