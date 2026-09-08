# Copyright 2024 Camptocamp
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64

from odoo.orm.model_classes import add_to_registry
from odoo.tools import mute_logger

from odoo.addons.edi_core_oca.tests.common import EDIBackendCommonTestCase

LOGGERS = (
    "odoo.addons.edi_core_oca.models.edi_backend",
    "odoo.addons.queue_job.delay",
)
DEPRECATION_LOGGER = "odoo.addons.edi_exchange_deduplicate_oca.models.edi_exchange_type"


class EDIDeduplicateTestCase(EDIBackendCommonTestCase):
    @classmethod
    def _setup_records(cls):  # pylint:disable=missing-return
        super()._setup_records()
        # Load fake models
        from odoo.addons.edi_core_oca.tests.fake_models import EdiTestExecution

        add_to_registry(cls.registry, EdiTestExecution)
        cls.registry._setup_models__(cls.env.cr, ["edi.framework.test.execution"])
        cls.registry.init_models(
            cls.env.cr,
            ["edi.framework.test.execution"],
            {"models_to_check": True},
        )
        cls.addClassCleanup(cls.registry.__delitem__, "edi.framework.test.execution")
        cls.model = cls.env["ir.model"].search(
            [("model", "=", "edi.framework.test.execution")]
        )
        cls.exchange_type_out.write(
            {
                "exchange_file_auto_generate": True,
                "generate_model_id": cls.model.id,
                "send_model_id": cls.model.id,
                "output_validate_model_id": cls.model.id,
            }
        )
        cls.exchange_type_in.write(
            {
                "process_model_id": cls.model.id,
            }
        )

    @mute_logger(*LOGGERS)
    def test_deduplicate_on_send(self):
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
        record2 = self.backend.create_record(
            "test_csv_output",
            {
                "model": self.partner._name,
                "res_id": self.partner.id,
            },
        )
        record3 = self.backend.create_record(
            "test_csv_output",
            {
                "model": self.partner._name,
                "res_id": self.partner.id,
            },
        )
        records = record1 + record2
        self.backend._check_output_exchange_sync()
        # Because we just sent the last record, so the others should be "obsolete"
        for record in records:
            self.assertEqual(record.edi_exchange_state, "obsolete")
        self.assertEqual(record3.edi_exchange_state, "output_sent")

    @mute_logger(*LOGGERS)
    def test_no_deduplicate_on_send(self):
        self.exchange_type_out.write(
            {
                "deduplicate_on_exchange": False,
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
        record3 = self.backend.create_record(
            "test_csv_output",
            {
                "model": self.partner._name,
                "res_id": self.partner.id,
            },
        )
        records = record1 + record2 + record3
        self.backend._check_output_exchange_sync()
        # All the records should be "output_sent"
        for record in records:
            self.assertEqual(record.edi_exchange_state, "output_sent")

    @mute_logger(*LOGGERS)
    def test_block_obsolescence(self):
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
        record2 = self.backend.create_record(
            "test_csv_output",
            {
                "model": self.partner._name,
                "res_id": self.partner.id,
                # Checking
                "block_obsolescence": True,
            },
        )
        record3 = self.backend.create_record(
            "test_csv_output",
            {
                "model": self.partner._name,
                "res_id": self.partner.id,
            },
        )
        self.backend._check_output_exchange_sync()
        # Normally, record2 has been "obsolete"
        # But with block_obsolescence = True, it will be "output_sent" too
        self.assertEqual(record1.edi_exchange_state, "obsolete")
        self.assertEqual(record2.edi_exchange_state, "output_sent")
        self.assertEqual(record3.edi_exchange_state, "output_sent")

    @mute_logger(*LOGGERS)
    def test_deduplicate_input_records(self):
        """Received records without a related record supersede each other.

        Scenario:
            1. Receive three records of the same input type, none linked to
               an Odoo record, before any of them is processed.
            2. Run the input sync.
        Expected:
            - The two oldest records are obsolete, the newest one is
              processed.
        """
        self.exchange_type_in.write(
            {
                "deduplicate_on_exchange": True,
            }
        )
        record1 = self.backend.create_record(
            "test_csv_input",
            {
                "edi_exchange_state": "input_received",
                "exchange_file": base64.b64encode(b"data"),
                "exchange_filename": "input.csv",
            },
        )
        record2 = self.backend.create_record(
            "test_csv_input",
            {
                "edi_exchange_state": "input_received",
                "exchange_file": base64.b64encode(b"data"),
                "exchange_filename": "input.csv",
            },
        )
        record3 = self.backend.create_record(
            "test_csv_input",
            {
                "edi_exchange_state": "input_received",
                "exchange_file": base64.b64encode(b"data"),
                "exchange_filename": "input.csv",
            },
        )
        # No related record: the newest one supersedes all the pending ones
        self.assertEqual(record1.edi_exchange_state, "obsolete")
        self.assertEqual(record2.edi_exchange_state, "obsolete")
        self.assertEqual(record3.edi_exchange_state, "input_received")
        self.backend._check_input_exchange_sync()
        # The obsolete records are skipped, only the last one is processed
        self.assertEqual(record1.edi_exchange_state, "obsolete")
        self.assertEqual(record2.edi_exchange_state, "obsolete")
        self.assertEqual(record3.edi_exchange_state, "input_processed")

    @mute_logger(*LOGGERS)
    def test_deduplicate_input_records_same_record_only(self):
        """A received record only supersedes the ones for the same record.

        Scenario:
            1. Receive a record for partner A, one for partner B, then
               another one for partner A.
        Expected:
            - Only the first record for partner A is obsolete.
        """
        self.exchange_type_in.write(
            {
                "deduplicate_on_exchange": True,
            }
        )
        other_partner = self.env["res.partner"].create({"name": "EDI EXC OTHER"})
        record1 = self.backend.create_record(
            "test_csv_input",
            {
                "edi_exchange_state": "input_received",
                "exchange_file": base64.b64encode(b"data"),
                "exchange_filename": "input.csv",
                "model": self.partner._name,
                "res_id": self.partner.id,
            },
        )
        record2 = self.backend.create_record(
            "test_csv_input",
            {
                "edi_exchange_state": "input_received",
                "exchange_file": base64.b64encode(b"data"),
                "exchange_filename": "input.csv",
                "model": other_partner._name,
                "res_id": other_partner.id,
            },
        )
        record3 = self.backend.create_record(
            "test_csv_input",
            {
                "edi_exchange_state": "input_received",
                "exchange_file": base64.b64encode(b"data"),
                "exchange_filename": "input.csv",
                "model": self.partner._name,
                "res_id": self.partner.id,
            },
        )
        self.assertEqual(record1.edi_exchange_state, "obsolete")
        self.assertEqual(record2.edi_exchange_state, "input_received")
        self.assertEqual(record3.edi_exchange_state, "input_received")

    @mute_logger(*LOGGERS)
    def test_deduplicate_input_records_keeps_processed(self):
        """Processed and failed records are never marked as obsolete.

        Scenario:
            1. Receive a record and process it.
            2. Receive a record and have it fail.
            3. Receive a third record.
        Expected:
            - The processed and the failed records keep their state.
        """
        self.exchange_type_in.write(
            {
                "deduplicate_on_exchange": True,
            }
        )
        record1 = self.backend.create_record(
            "test_csv_input",
            {
                "edi_exchange_state": "input_received",
                "exchange_file": base64.b64encode(b"data"),
                "exchange_filename": "input.csv",
            },
        )
        self.backend._check_input_exchange_sync()
        self.assertEqual(record1.edi_exchange_state, "input_processed")
        record2 = self.backend.create_record(
            "test_csv_input",
            {
                "edi_exchange_state": "input_received",
                "exchange_file": base64.b64encode(b"data"),
                "exchange_filename": "input.csv",
            },
        )
        record2.edi_exchange_state = "input_processed_error"
        self.backend.create_record(
            "test_csv_input",
            {
                "edi_exchange_state": "input_received",
                "exchange_file": base64.b64encode(b"data"),
                "exchange_filename": "input.csv",
            },
        )
        self.assertEqual(record1.edi_exchange_state, "input_processed")
        self.assertEqual(record2.edi_exchange_state, "input_processed_error")

    @mute_logger(*LOGGERS)
    def test_no_deduplicate_input_records(self):
        """Without the option, every received record is processed."""
        record1 = self.backend.create_record(
            "test_csv_input",
            {
                "edi_exchange_state": "input_received",
                "exchange_file": base64.b64encode(b"data"),
                "exchange_filename": "input.csv",
            },
        )
        record2 = self.backend.create_record(
            "test_csv_input",
            {
                "edi_exchange_state": "input_received",
                "exchange_file": base64.b64encode(b"data"),
                "exchange_filename": "input.csv",
            },
        )
        self.assertEqual(record1.edi_exchange_state, "input_received")
        self.assertEqual(record2.edi_exchange_state, "input_received")
        self.backend._check_input_exchange_sync()
        self.assertEqual(record1.edi_exchange_state, "input_processed")
        self.assertEqual(record2.edi_exchange_state, "input_processed")

    def test_deduplicate_on_send_deprecated_alias_on_create(self):
        """Creating a type with the old flag logs a deprecation warning."""
        with self.assertLogs(DEPRECATION_LOGGER, level="WARNING") as log:
            exchange_type = self._create_exchange_type(
                name="Test CSV deprecated",
                code="test_csv_deprecated",
                direction="output",
                deduplicate_on_send=True,
            )
        self.assertIn("deduplicate_on_send' is deprecated", log.output[0])
        self.assertTrue(exchange_type.deduplicate_on_exchange)

    def test_deduplicate_on_send_deprecated_alias_on_write(self):
        """The old flag still works, and writing it logs a deprecation warning."""
        with self.assertLogs(DEPRECATION_LOGGER, level="WARNING") as log:
            self.exchange_type_out.write({"deduplicate_on_send": True})
        self.assertIn("deduplicate_on_send' is deprecated", log.output[0])
        self.assertTrue(self.exchange_type_out.deduplicate_on_exchange)
        self.assertIn(
            self.exchange_type_out,
            self.env["edi.exchange.type"].search([("deduplicate_on_send", "=", True)]),
        )
        self.exchange_type_out.deduplicate_on_exchange = False
        self.assertFalse(self.exchange_type_out.deduplicate_on_send)
