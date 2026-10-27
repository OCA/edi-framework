# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging

from psycopg2.extras import execute_values

_logger = logging.getLogger(__name__)

BATCH_SIZE = 1000
TRACEBACK_PREFIX = "Traceback (most recent call last)"


def _get_exception_msg(traceback):
    lines = traceback.rstrip().splitlines()
    last_frame = max(
        (i for i, line in enumerate(lines) if line.startswith("  File ")),
        default=-1,
    )
    exc_lines = [
        line for line in lines[last_frame + 1 :] if line and not line.startswith(" ")
    ]
    if last_frame == -1 or not exc_lines:
        return traceback
    head, sep, tail = exc_lines[0].partition(": ")
    exc_lines[0] = tail if sep else head
    return "\n".join(exc_lines).strip()


def migrate(cr, version):
    """Move the traceback stored in exchange_error before the split."""
    last_id = updated = 0
    while True:
        cr.execute(
            """
            SELECT id, exchange_error
            FROM edi_exchange_record
            WHERE exchange_error_traceback IS NULL
              AND exchange_error LIKE %s
              AND id > %s
            ORDER BY id
            LIMIT %s
            """,
            (TRACEBACK_PREFIX + "%", last_id, BATCH_SIZE),
        )
        rows = cr.fetchall()
        if not rows:
            break
        execute_values(
            cr,
            """
            UPDATE edi_exchange_record AS record
            SET exchange_error = data.error,
                exchange_error_traceback = data.traceback
            FROM (VALUES %s) AS data (id, error, traceback)
            WHERE record.id = data.id
            """,
            [(rec_id, _get_exception_msg(error), error) for rec_id, error in rows],
        )
        last_id = rows[-1][0]
        updated += len(rows)
    _logger.info("Moved the traceback of %d exchange records", updated)
