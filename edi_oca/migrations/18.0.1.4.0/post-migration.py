# Copyright 2025 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Create exchange record related records from existing main records."""
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO edi_exchange_related_record (
            exchange_record_id, res_id, model
        )
            SELECT eer.id, eer.res_id, eer.model
            FROM edi_exchange_record eer
                LEFT JOIN edi_exchange_related_record eerr
                    ON eerr.exchange_record_id = eer.id
            WHERE eerr.id IS NULL
                AND eer.res_id IS NOT NULL
                AND eer.model IS NOT NULL
    """,
    )
