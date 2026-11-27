# Copyright 2026 Camptocamp SA (https://camptocamp.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Migrate ``edi_exchange_state`` values from 'obsolete' to 'cancelled'"""
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE edi_exchange_record
        SET edi_exchange_state = 'cancelled'
        WHERE edi_exchange_state = 'obsolete'
        """,
    )
