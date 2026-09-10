# Copyright 2024 Camptocamp
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.exceptions import ValidationError
from odoo.tools import mute_logger

from .test_edi_duplicate import EDIDeduplicateTestCase

LOGGERS = (
    "odoo.addons.edi_core_oca.models.edi_backend",
    "odoo.addons.queue_job.delay",
)


class TestDeduplicateOnExchangeRecordStatus(EDIDeduplicateTestCase):
    def test_configured_statuses_must_exist_in_selection(self):
        with self.assertRaisesRegex(ValidationError, "Invalid exchange state"):
            self.exchange_type_out.write(
                {
                    "deduplicate_on_exchange_record_status": "new,not_a_state",
                }
            )

    def test_configured_statuses_accept_valid_values(self):
        # "obsolete" comes from this addon via selection_add on edi_exchange_state.
        self.exchange_type_out.write(
            {
                "deduplicate_on_exchange_record_status": (
                    "new, output_pending, obsolete"
                ),
            }
        )
        self.assertEqual(
            self.exchange_type_out.deduplicate_on_exchange_record_status,
            "new, output_pending, obsolete",
        )

    @mute_logger(*LOGGERS)
    def test_default_status_deduplicates_new_records(self):
        self.exchange_type_out.write(
            {
                "deduplicate_on_exchange": True,
            }
        )
        record1 = self.backend.create_record(
            "test_csv_output",
            {
                "model": self.partner._name,
                "res_id": self.partner.id,
            },
        )
        self.backend.create_record(
            "test_csv_output",
            {
                "model": self.partner._name,
                "res_id": self.partner.id,
            },
        )

        self.assertEqual(record1.edi_exchange_state, "obsolete")

    @mute_logger(*LOGGERS)
    def test_custom_status_filter_is_used_for_deduplication(self):
        self.exchange_type_out.write(
            {
                "deduplicate_on_exchange": True,
                "deduplicate_on_exchange_record_status": "output_pending",
            }
        )
        record1 = self.backend.create_record(
            "test_csv_output",
            {
                "model": self.partner._name,
                "res_id": self.partner.id,
            },
        )
        record2 = self.backend.create_record(
            "test_csv_output",
            {
                "model": self.partner._name,
                "res_id": self.partner.id,
            },
        )

        # "new" is not part of the configured list, so no deduplication yet.
        self.assertEqual(record1.edi_exchange_state, "new")

        record1.edi_exchange_state = "output_pending"
        self.backend.create_record(
            "test_csv_output",
            {
                "model": self.partner._name,
                "res_id": self.partner.id,
            },
        )

        self.assertEqual(record1.edi_exchange_state, "obsolete")
        self.assertEqual(record2.edi_exchange_state, "new")
