# Copyright 2026 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
import os

import psycopg2

from odoo.tools import SQL, human_size

_logger = logging.getLogger(__name__)


def _get_exchange_files_to_move(env, last_id, limit):
    record_model = env["edi.exchange.record"]
    env.cr.execute(
        SQL(
            """
            SELECT a.id, r.type_id, a.file_size, a.store_fname, a.checksum
            FROM ir_attachment a
            JOIN %(record_table)s r ON r.id = a.res_id
            WHERE a.res_model = %(res_model)s
                AND a.res_field = %(res_field)s
                AND a.type = 'binary'
                AND a.store_fname IS NOT NULL
                AND a.id > %(last_id)s
            ORDER BY a.id
            LIMIT %(limit)s
            """,
            record_table=SQL.identifier(record_model._table),
            res_model=record_model._name,
            res_field="exchange_file",
            last_id=last_id,
            limit=limit,
        )
    )
    return env.cr.fetchall()


def _read_exchange_file(env, fname, checksum):
    attachment_model = env["ir.attachment"]
    full_path = attachment_model._full_path(fname)
    if not os.path.isfile(full_path):
        return None, "missing"
    with open(full_path, "rb") as file:
        data = file.read()
    if attachment_model._compute_checksum(data) != checksum:
        return None, "mismatched"
    return data, "moved"


def move_exchange_file_contents_to_db(env, batch_size=1000):
    attachment_model = env["ir.attachment"]
    attachment_model.flush_model(
        [
            "res_model",
            "res_field",
            "res_id",
            "type",
            "file_size",
            "store_fname",
            "checksum",
        ]
    )
    env["edi.exchange.record"].flush_model(["type_id"])
    counts = {"moved": 0, "excluded": 0, "missing": 0, "mismatched": 0}
    moved_size = 0
    last_id = 0
    while rows := _get_exchange_files_to_move(env, last_id, batch_size):
        last_id = rows[-1][0]
        exchange_types = {
            exchange_type.id: exchange_type
            for exchange_type in env["edi.exchange.type"].browse(
                list({row[1] for row in rows})
            )
        }
        values, fnames = [], []
        for attachment_id, type_id, file_size, fname, checksum in rows:
            if not exchange_types[type_id]._should_store_file_content_in_db(file_size):
                counts["excluded"] += 1
                continue
            data, status = _read_exchange_file(env, fname, checksum)
            counts[status] += 1
            if data is None:
                continue
            values.append((attachment_id, psycopg2.Binary(data)))
            fnames.append(fname)
            moved_size += len(data)
        if not values:
            continue
        env.cr.execute_values(
            """
            UPDATE ir_attachment a
            SET db_datas = v.data, store_fname = NULL
            FROM (VALUES %s) AS v(id, data)
            WHERE a.id = v.id
            """,
            values,
            page_size=batch_size,
        )
        for fname in fnames:
            attachment_model._file_delete(fname)
    attachment_model.invalidate_model(["db_datas", "store_fname", "raw", "datas"])
    _logger.info(
        "EDI exchange file contents moved to the database: %s (%s). Skipped: %s "
        "excluded by their exchange type, %s missing from the filestore, %s not "
        "matching their checksum.",
        counts["moved"],
        human_size(moved_size) or "0 bytes",
        counts["excluded"],
        counts["missing"],
        counts["mismatched"],
    )
    return counts


def post_init_hook(env):
    move_exchange_file_contents_to_db(env)
