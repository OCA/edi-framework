# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def adapt_to_refactor(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE edi_exchange_type eet
        SET exchange_type_group_id = eb.backend_group_id
        FROM edi_backend eb
        WHERE eet.backend_id = eb.id AND eb.backend_group_id IS NOT NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    adapt_to_refactor(env)
    openupgrade.load_data(
        env.cr, "custom_module", "migrations/16.0.1.0.0/noupdate_changes.xml"
    )
