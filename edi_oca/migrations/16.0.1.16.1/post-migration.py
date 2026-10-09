# Copyright 2026 Camptocamp SA (http://www.camptocamp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


def migrate(cr, version):
    cr.execute(
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
