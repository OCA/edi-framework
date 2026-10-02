# Copyright 2026 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64
import json

from odoo.exceptions import UserError
from odoo.tests.common import RecordCapturer as RC

from .common import EDIExchangeRecordFileManagerCommon


class TestEDIExchangeRecordFileManager(EDIExchangeRecordFileManagerCommon):
    # ----------------------------------------------------------------------------------
    # Setup state
    # ----------------------------------------------------------------------------------

    def test_mode_is_mandatory_to_proceed_from_setup(self):
        """Ensures you cannot proceed from setup without a mode"""
        wizard = self._create_wizard(custom_values={"state": "setup", "mode": None})
        with self.assertRaises(UserError):
            wizard.button_proceed()

    # ----------------------------------------------------------------------------------
    # Edit state
    # ----------------------------------------------------------------------------------

    def test_edit_flow(self):
        """Tests workflow ``setup`` -> ``edit`` -> ``done``"""
        wizard = self._create_wizard(
            custom_values={"state": "setup", "mode": "edit_in_place"}
        )
        record = wizard.exchange_record_id
        old_state = record.edi_exchange_state
        old_checksum = record.exchange_filechecksum
        old_filename = record.exchange_filename
        wizard.button_proceed()
        self.assertEqual(wizard.state, "edit")
        self.assertEqual(wizard.file_content, "Test")
        self.assertEqual(wizard.ace_mode, "txt")
        wizard.file_content = "Test 2"
        with RC(self.env["mail.message"], [("res_id", "=", record.id)]) as rc:
            wizard.button_proceed()
        self.assertEqual(wizard.state, "done")
        self.assertEqual(record._get_file_content(), "Test 2")
        self.assertNotEqual(record.exchange_filechecksum, old_checksum)
        self.assertEqual(record.exchange_filename, old_filename)
        self.assertEqual(record.edi_exchange_state, old_state)
        self.assertEqual(len(rc.records), 1)
        self.assertEqual(
            str(rc.records.body), "<p>File edited through file manager.</p>"
        )

    def test_edit_respects_exchange_type_encoding(self):
        """Checks that updating the file content respects the exchange encoding"""
        encoding = "ISO-8859-1"
        self.exchange_type_in.encoding = encoding
        record = self._create_record(
            self.exchange_type_in.code,
            "input_processed_error",
            content="caffè".encode(encoding),
        )
        wizard = self._create_wizard(
            record, custom_values={"state": "setup", "mode": "edit_in_place"}
        )
        wizard.button_proceed()
        self.assertEqual(wizard.file_content, "caffè")
        wizard.file_content = "perché"
        wizard.button_proceed()
        self.assertEqual(
            record._get_file_content(as_bytes=True), "perché".encode(encoding)
        )

    def test_edit_not_encodable_content(self):
        """Checks an error is raised if new file content doesn't match the encoding"""
        encoding = "ASCII"
        self.exchange_type_out.encoding = encoding
        record = self._create_record(
            self.exchange_type_out.code, "output_sent_and_error", content="caffe"
        )
        wizard = self._create_wizard(
            record, custom_values={"state": "setup", "mode": "edit_in_place"}
        )
        wizard.button_proceed()
        self.assertEqual(wizard.file_content, "caffe")
        wizard.file_content = "caffè"
        with self.assertRaises(UserError):
            wizard.button_proceed()
        self.assertEqual(record._get_file_content(), "caffe")

    # ----------------------------------------------------------------------------------
    # Replace state
    # ----------------------------------------------------------------------------------

    def test_replace_flow(self):
        """Tests workflow ``setup`` -> ``replace`` -> ``done``"""
        wizard = self._create_wizard(
            custom_values={"state": "setup", "mode": "download_and_replace"}
        )
        record = wizard.exchange_record_id
        old_state = record.edi_exchange_state
        old_checksum = record.exchange_filechecksum
        old_filename = record.exchange_filename
        wizard.button_proceed()
        self.assertEqual(wizard.state, "replace")
        # a new file is needed to proceed
        with self.assertRaises(UserError):
            wizard.button_proceed()
        wizard.new_file = base64.b64encode(b"new,file\n")
        wizard.new_filename = "whatever.csv"
        with RC(self.env["mail.message"], [("res_id", "=", record.id)]) as rc:
            wizard.button_proceed()
        self.assertEqual(wizard.state, "done")
        self.assertEqual(record._get_file_content(), "new,file\n")
        self.assertNotEqual(record.exchange_filechecksum, old_checksum)
        self.assertEqual(record.exchange_filename, old_filename)
        self.assertEqual(record.edi_exchange_state, old_state)
        self.assertEqual(len(rc.records), 1)
        self.assertEqual(
            str(rc.records.body), "<p>File replaced through file manager.</p>"
        )

    # ----------------------------------------------------------------------------------
    # Encoding validation on replace
    # ----------------------------------------------------------------------------------

    def test_replace_file_with_valid_encoding(self):
        self.exchange_type_in.encoding = "UTF-8"
        wizard = self._create_wizard(custom_values={"state": "replace"})
        record = wizard.exchange_record_id
        old_content = record._get_file_content(as_bytes=True)
        new_content = "Città e qualità".encode()
        wizard.new_file = base64.b64encode(new_content)
        wizard._execute_replace()
        current_content = record._get_file_content(as_bytes=True)
        self.assertEqual(current_content, new_content)
        self.assertNotEqual(current_content, old_content)

    def test_replace_file_with_invalid_encoding(self):
        self.exchange_type_in.encoding = "UTF-8"
        wizard = self._create_wizard(custom_values={"state": "replace"})
        record = wizard.exchange_record_id
        old_content = record._get_file_content(as_bytes=True)
        new_content = b"\xff\xfe"
        wizard.new_file = base64.b64encode(new_content)
        with self.assertRaisesRegex(
            UserError, "The file is not consistent with the exchange type encoding"
        ):
            wizard._execute_replace()
        current_content = record._get_file_content(as_bytes=True)
        self.assertNotEqual(current_content, new_content)
        self.assertEqual(current_content, old_content)

    # ----------------------------------------------------------------------------------
    # Done state
    # ----------------------------------------------------------------------------------

    def test_exchange_record_state_changed_while_wizard_is_open(self):
        """Test the "Proceed" button raises an error if the Exc Rec state changed"""
        for state in ("setup", "edit", "replace"):
            with self.subTest(state=state):
                record = self._create_record(
                    self.exchange_type_out.code, "output_sent_and_error", content="Test"
                )
                wizard = self._create_wizard(record, custom_values={"state": state})
                record.edi_exchange_state = "output_sent"
                with self.assertRaises(UserError):
                    wizard.button_proceed()

    def test_proceed_after_done_refused(self):
        """Test the "Proceed" button raises an error if used on a "done" wizard"""
        wizard = self._create_wizard(custom_values={"state": "done"})
        with self.assertRaises(UserError):
            wizard.button_proceed()

    # ----------------------------------------------------------------------------------
    # Ace mode tools
    # ----------------------------------------------------------------------------------

    def test_ace_mode_from_exc_record_file_extension(self):
        """Test the ``ace_mode`` guessing from the Exc Rec file extension"""
        for ext, mode in (
            self.env["edi.exchange.record.file.manager"]
            ._get_extension_to_ace_mode_map()
            .items()
        ):
            with self.subTest(exc_record_file_ext=ext, expected_ace_mode=mode):
                record = self._create_record(
                    self.exchange_type_out.code,
                    "output_sent_and_error",
                    content="Test",
                    custom_values={"exchange_filename": f"something.{ext}"},
                )
                wizard = self._create_wizard(record)
                self.assertEqual(wizard._guess_ace_mode(), mode)

    def test_ace_mode_from_exc_type_file_extension(self):
        """Test the ``ace_mode`` guessing from the Exc Type file extension"""
        for ext, mode in (
            self.env["edi.exchange.record.file.manager"]
            ._get_extension_to_ace_mode_map()
            .items()
        ):
            with self.subTest(exc_type_file_ext=ext, expected_ace_mode=mode):
                self.exchange_type_out.exchange_file_ext = ext
                record = self._create_record(
                    self.exchange_type_out.code,
                    "output_sent_and_error",
                    content="Test",
                    custom_values={"exchange_filename": "something"},
                )
                wizard = self._create_wizard(record)
                self.assertEqual(wizard._guess_ace_mode(), mode)

    def test_ace_mode_from_exc_record_file_content(self):
        """Test the ``ace_mode`` guessing from the Exc Rec content"""
        for content, mode in [
            ("\n    <p/>", "xml"),
            (json.dumps({"test": "1"}), "javascript"),
            (json.dumps(["test"]), "javascript"),
            (json.dumps(["test"]) + " something to make this invalid", "txt"),
            ("Test", "txt"),
            ("", "txt"),
        ]:
            with self.subTest(exc_record_file_content=content, expected_ace_mode=mode):
                record = self._create_record(
                    self.exchange_type_out.code,
                    "output_sent_and_error",
                    content=content,
                )
                wizard = self._create_wizard(record)
                self.assertEqual(wizard._guess_ace_mode(), mode)
