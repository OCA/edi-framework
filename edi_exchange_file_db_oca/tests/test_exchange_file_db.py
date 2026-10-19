# Copyright 2026 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64
import os
from unittest.mock import patch

from odoo.addons.edi_oca.tests.common import EDIBackendCommonTestCase

from ..hooks import move_exchange_file_contents_to_db
from ..models.edi_exchange_type import MAX_SIZE_PARAM


class TestExchangeFileDb(EDIBackendCommonTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Attachment = cls.env["ir.attachment"]
        cls.ExchangeRecord = cls.env["edi.exchange.record"]

    def _create_record(self, content=None, exchange_type=None):
        exchange_type = exchange_type or self.exchange_type_out
        vals = {"model": self.partner._name, "res_id": self.partner.id}
        if content is not None:
            vals["exchange_file"] = base64.b64encode(content)
        return self.backend.create_record(exchange_type.code, vals)

    def _get_attachment(self, record):
        return self.Attachment.search(
            [
                ("res_model", "=", record._name),
                ("res_field", "=", "exchange_file"),
                ("res_id", "=", record.id),
            ]
        )

    def assertInDb(self, record, content):
        attachment = self._get_attachment(record)
        self.assertFalse(attachment.store_fname)
        self.assertEqual(attachment.db_datas, content)
        record.invalidate_recordset(["exchange_file"])
        self.assertEqual(record._get_file_content(as_bytes=True), content)

    def assertInFilestore(self, record, content):
        attachment = self._get_attachment(record)
        self.assertTrue(attachment.store_fname)
        self.assertFalse(attachment.db_datas)
        self.assertEqual(attachment._file_read(attachment.store_fname), content)
        record.invalidate_recordset(["exchange_file"])
        self.assertEqual(record._get_file_content(as_bytes=True), content)

    def test_file_in_db(self):
        record = self._create_record(b"in database")
        self.assertInDb(record, b"in database")

    def test_file_in_filestore_when_disabled(self):
        self.exchange_type_out.store_file_content_in_db = False
        record = self._create_record(b"in filestore")
        self.assertInFilestore(record, b"in filestore")

    def test_global_max_size(self):
        self.env["ir.config_parameter"].sudo().set_param(MAX_SIZE_PARAM, "1")
        small = self._create_record(b"x" * 1024)
        big = self._create_record(b"x" * 1025)
        self.assertInDb(small, b"x" * 1024)
        self.assertInFilestore(big, b"x" * 1025)

    def test_type_max_size_overrides_global(self):
        self.env["ir.config_parameter"].sudo().set_param(MAX_SIZE_PARAM, "1")
        self.exchange_type_out.file_content_db_max_size = 2
        record = self._create_record(b"x" * 2048)
        self.assertInDb(record, b"x" * 2048)
        record = self._create_record(b"x" * 2049)
        self.assertInFilestore(record, b"x" * 2049)

    def test_rewrite(self):
        record = self._create_record(b"before")
        record.exchange_file = base64.b64encode(b"after")
        self.assertInDb(record, b"after")
        self.exchange_type_out.store_file_content_in_db = False
        record.exchange_file = base64.b64encode(b"back to filestore")
        self.assertInFilestore(record, b"back to filestore")
        self.exchange_type_out.store_file_content_in_db = True
        record.exchange_file = base64.b64encode(b"back to database")
        self.assertInDb(record, b"back to database")

    def test_create_batch(self):
        self.exchange_type_in.store_file_content_in_db = False
        records = self.ExchangeRecord.create(
            [
                {
                    "backend_id": self.backend.id,
                    "type_id": exchange_type.id,
                    "exchange_file": base64.b64encode(content),
                }
                for exchange_type, content in (
                    (self.exchange_type_out, b"first"),
                    (self.exchange_type_in, b"second"),
                    (self.exchange_type_out, b"third"),
                )
            ]
        )
        self.assertEqual(records[1].type_id, self.exchange_type_in)
        self.assertInDb(records[0], b"first")
        self.assertInFilestore(records[1], b"second")
        self.assertInDb(records[2], b"third")
        self.assertFalse(records.env.context.get("edi_exchange_file_content_in_db"))

    def test_write_batch(self):
        self.exchange_type_in.store_file_content_in_db = False
        records = self._create_record() | self._create_record(
            exchange_type=self.exchange_type_in
        )
        records.write({"exchange_file": base64.b64encode(b"both")})
        self.assertInDb(records[0], b"both")
        self.assertInFilestore(records[1], b"both")

    def test_attachment_outside_exchange_file(self):
        record = self._create_record()
        attachment = self.Attachment.create(
            {
                "name": "chatter",
                "res_model": record._name,
                "res_id": record.id,
                "raw": b"chatter",
            }
        )
        self.assertTrue(attachment.store_fname)
        self.assertFalse(attachment.db_datas)

    def test_other_attachment_rewrite(self):
        attachment = self.Attachment.create(
            {
                "name": "partner",
                "res_model": self.partner._name,
                "res_id": self.partner.id,
                "raw": b"partner",
            }
        )
        attachment.raw = b"partner rewritten"
        self.assertTrue(attachment.store_fname)
        self.assertFalse(attachment.db_datas)
        self.assertEqual(attachment.raw, b"partner rewritten")

    def test_search_exchange_file(self):
        with_file = self._create_record(b"content")
        without_file = self._create_record()
        domain = [("id", "in", (with_file | without_file).ids)]
        self.assertEqual(
            self.ExchangeRecord.search(domain + [("exchange_file", "=", False)]),
            without_file,
        )
        self.assertEqual(
            self.ExchangeRecord.search(domain + [("exchange_file", "!=", False)]),
            with_file,
        )

    def test_move_to_db(self):
        self.exchange_type_out.store_file_content_in_db = False
        record = self._create_record(b"move me")
        attachment = self._get_attachment(record)
        fname = attachment.store_fname
        checksum = attachment.checksum
        self.exchange_type_out.store_file_content_in_db = True
        counts = move_exchange_file_contents_to_db(self.env)
        self.assertEqual(
            counts, {"moved": 1, "excluded": 0, "missing": 0, "mismatched": 0}
        )
        self.assertInDb(record, b"move me")
        self.assertEqual(attachment.checksum, checksum)
        checklist = os.path.join(self.Attachment._full_path("checklist"), fname)
        self.assertTrue(os.path.isfile(checklist))

    def test_move_to_db_respects_max_size(self):
        self.exchange_type_out.store_file_content_in_db = False
        record = self._create_record(b"x" * 2048)
        self.exchange_type_out.write(
            {"store_file_content_in_db": True, "file_content_db_max_size": 1}
        )
        counts = move_exchange_file_contents_to_db(self.env)
        self.assertEqual(
            counts, {"moved": 0, "excluded": 1, "missing": 0, "mismatched": 0}
        )
        self.assertInFilestore(record, b"x" * 2048)

    def test_move_to_db_skips_missing_and_mismatched(self):
        self.exchange_type_out.store_file_content_in_db = False
        missing = self._get_attachment(self._create_record(b"missing"))
        mismatched_record = self._create_record(b"mismatched")
        mismatched = self._get_attachment(mismatched_record)
        self.env.cr.execute(
            "UPDATE ir_attachment SET store_fname = %s WHERE id = %s",
            ("00/does-not-exist", missing.id),
        )
        self.env.cr.execute(
            "UPDATE ir_attachment SET checksum = %s WHERE id = %s",
            ("0" * 40, mismatched.id),
        )
        self.Attachment.invalidate_model(["store_fname", "checksum"])
        self.exchange_type_out.store_file_content_in_db = True
        counts = move_exchange_file_contents_to_db(self.env)
        self.assertEqual(
            counts, {"moved": 0, "excluded": 0, "missing": 1, "mismatched": 1}
        )
        self.assertEqual(missing.store_fname, "00/does-not-exist")
        self.assertInFilestore(mismatched_record, b"mismatched")

    def test_file_content_json_indented(self):
        record = self._create_record(b'{"a": 1, "b": "\xc3\xa9"}')
        record = record.with_context(bin_size=True)
        self.assertEqual(record.exchange_file_content_format, "json")
        self.assertEqual(record.exchange_file_content, '{\n  "a": 1,\n  "b": "\xe9"\n}')

    def test_file_content_xml(self):
        content = b'<?xml version="1.0"?>\n<Invoice><ID>1</ID></Invoice>'
        record = self._create_record(content)
        self.assertEqual(record.exchange_file_content_format, "xml")
        self.assertEqual(record.exchange_file_content, content.decode())

    def test_file_content_text(self):
        record = self._create_record(b"a;b\n1;2\n")
        self.assertEqual(record.exchange_file_content_format, "text")
        self.assertEqual(record.exchange_file_content, "a;b\n1;2\n")

    def test_file_content_wrong_encoding(self):
        content = "referencia;descripción\nCT0118;tuerca\n"
        record = self._create_record(content.encode("latin-1"))
        self.assertEqual(record.exchange_file_content_format, "text")
        self.assertEqual(record.exchange_file_content, content)

    def test_file_content_binary_signature(self):
        self.exchange_type_out.encoding = "latin-1"
        record = self._create_record(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj")
        self.assertEqual(record.exchange_file_content_format, "binary")
        self.assertEqual(record.exchange_file_content_mimetype, "application/pdf")
        self.assertFalse(record.exchange_file_content)

    def test_file_content_binary_nul(self):
        self.exchange_type_out.encoding = "latin-1"
        record = self._create_record(b"\x1f\x8b\x08\x00\x00\x00\x00\x00")
        self.assertEqual(record.exchange_file_content_format, "binary")
        self.assertFalse(record.exchange_file_content)

    def test_file_content_too_large(self):
        record = self._create_record(b'{"a": 1}')
        with patch.object(
            type(self.ExchangeRecord),
            "_get_exchange_file_display_max_size",
            return_value=4,
        ):
            record.invalidate_recordset(["exchange_file_content_too_large"])
            self.assertTrue(record.exchange_file_content_too_large)
            self.assertFalse(record.exchange_file_content_format)
            self.assertFalse(record.exchange_file_content)

    def test_file_content_empty(self):
        record = self._create_record()
        self.assertFalse(record.exchange_file_content_format)
        self.assertFalse(record.exchange_file_content_too_large)
