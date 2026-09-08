# Copyright 2026 Camptocamp
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tools.sql import column_exists, rename_column


def migrate(cr, version):
    # ``deduplicate_on_send`` became a related alias of the new
    # ``deduplicate_on_exchange``: carry the configured value over.
    if column_exists(cr, "edi_exchange_type", "deduplicate_on_send") and not (
        column_exists(cr, "edi_exchange_type", "deduplicate_on_exchange")
    ):
        rename_column(
            cr, "edi_exchange_type", "deduplicate_on_send", "deduplicate_on_exchange"
        )
