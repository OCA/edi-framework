# Copyright 2024 Camptocamp SA (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    if not version:
        return

    cr.execute(
        """
        UPDATE edi_exchange_record AS e
        SET storage_id = b.storage_id
        FROM edi_backend AS b
        WHERE e.backend_id = b.id;
        """
    )
