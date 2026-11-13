# Copyright 2026 Camptocamp SA (http://www.camptocamp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Backfill the stored flag for records already holding a file.
    env.cr.execute(
        """
        UPDATE edi_exchange_record AS record
        SET has_exchange_file = TRUE
        WHERE EXISTS (
            SELECT 1
            FROM ir_attachment AS attachment
            WHERE attachment.res_model = 'edi.exchange.record'
              AND attachment.res_field = 'exchange_file'
              AND attachment.res_id = record.id
        )
        """
    )
