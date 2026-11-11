# Copyright 2026 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64
import codecs
import contextlib
import json

import chardet

from odoo import api, fields, models
from odoo.tools.mimetypes import guess_mimetype

TEXT_MIMETYPES = ("application/octet-stream", "application/xml", "image/svg+xml")
DISPLAY_MAX_SIZE = 1024 * 1024


class EDIExchangeRecord(models.Model):
    _inherit = "edi.exchange.record"

    exchange_file_content = fields.Text(
        string="File Content",
        compute="_compute_exchange_file_content",
        help="Content of the exchange file, when it is text. JSON is indented.",
    )
    exchange_file_content_format = fields.Selection(
        selection=[
            ("json", "JSON"),
            ("xml", "XML"),
            ("text", "Text"),
            ("binary", "Binary"),
        ],
        compute="_compute_exchange_file_content",
        help="Empty when the file is too large or missing.",
    )
    exchange_file_content_mimetype = fields.Char(
        string="File Type",
        compute="_compute_exchange_file_content",
    )
    exchange_file_content_too_large = fields.Boolean(
        compute="_compute_exchange_file_content",
    )

    @api.depends("exchange_file")
    def _compute_exchange_file_content(self):
        for record in self:
            record.update(
                record.with_context(bin_size=False)._get_exchange_file_display_values()
            )

    def _create(self, data_list):
        in_db = self._get_exchange_file_content_in_db_flags(data_list)
        if not any(in_db):
            return super()._create(data_list)
        records = {}
        for flag in (True, False):
            group = [
                data for data, db in zip(data_list, in_db, strict=True) if db == flag
            ]
            if group:
                records[flag] = iter(
                    super(
                        EDIExchangeRecord,
                        self.with_context(edi_exchange_file_content_in_db=flag),
                    )
                    ._create(group)
                    .ids
                )
        return self.browse([next(records[db]) for db in in_db])

    def write(self, vals):
        if "exchange_file" not in vals:
            return super().write(vals)
        vals = dict(vals)
        file = vals.pop("exchange_file")
        if vals:
            super().write(vals)
        size = self._get_exchange_file_size(file)
        db_records = self.filtered(
            lambda record: record.type_id._should_store_file_content_in_db(size)
        )
        for records, in_db in ((db_records, True), (self - db_records, False)):
            if records:
                super(
                    EDIExchangeRecord,
                    records.with_context(edi_exchange_file_content_in_db=in_db),
                ).write({"exchange_file": file})
        return True

    @api.model
    def _get_exchange_file_content_in_db_flags(self, data_list):
        stored_list = [data["stored"] for data in data_list]
        type_ids = {
            stored["type_id"]
            for stored in stored_list
            if stored.get("exchange_file") and stored.get("type_id")
        }
        exchange_types = {
            exchange_type.id: exchange_type
            for exchange_type in self.env["edi.exchange.type"].browse(list(type_ids))
        }
        empty_type = self.env["edi.exchange.type"]
        return [
            bool(stored.get("exchange_file"))
            and exchange_types.get(
                stored.get("type_id"), empty_type
            )._should_store_file_content_in_db(
                self._get_exchange_file_size(stored["exchange_file"])
            )
            for stored in stored_list
        ]

    @api.model
    def _get_exchange_file_size(self, file):
        return len(base64.b64decode(file or b""))

    @api.model
    def _get_exchange_file_display_max_size(self):
        return DISPLAY_MAX_SIZE

    def _get_exchange_file_encoding(self):
        self.ensure_one()
        return codecs.lookup(self.type_id.encoding or "utf-8").name

    def _is_exchange_file_binary(self, raw):
        mimetype = guess_mimetype(raw)
        if mimetype not in TEXT_MIMETYPES and not mimetype.startswith("text/"):
            return True
        encoding = self._get_exchange_file_encoding()
        return not encoding.startswith(("utf-16", "utf-32")) and b"\x00" in raw[:1024]

    def _decode_exchange_file(self, raw):
        encoding = self._get_exchange_file_encoding()
        with contextlib.suppress(UnicodeDecodeError):
            return raw.decode(encoding)
        detected_encoding = chardet.detect(raw)["encoding"]
        if detected_encoding:
            with contextlib.suppress(UnicodeDecodeError, LookupError):
                return raw.decode(detected_encoding)
        return raw.decode(encoding, errors="replace")

    def _get_exchange_file_display_values(self):
        self.ensure_one()
        values = {
            "exchange_file_content": False,
            "exchange_file_content_format": False,
            "exchange_file_content_too_large": False,
            "exchange_file_content_mimetype": False,
        }
        raw = self._get_file_content(as_bytes=True)
        if not raw:
            return values
        if self._is_exchange_file_binary(raw):
            values["exchange_file_content_format"] = "binary"
            values["exchange_file_content_mimetype"] = guess_mimetype(raw)
            return values
        if len(raw) > self._get_exchange_file_display_max_size():
            values["exchange_file_content_too_large"] = True
            return values
        content = self._decode_exchange_file(raw)
        try:
            values["exchange_file_content"] = json.dumps(
                json.loads(content), indent=2, ensure_ascii=False
            )
            values["exchange_file_content_format"] = "json"
        except ValueError:
            values["exchange_file_content"] = content
            values["exchange_file_content_format"] = (
                "xml" if guess_mimetype(raw) == "application/xml" else "text"
            )
        return values
