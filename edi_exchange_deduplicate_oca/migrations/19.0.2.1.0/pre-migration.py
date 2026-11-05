# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Obsolete records are now deleted by the base autovacuum cron
    openupgrade.delete_records_safely_by_xml_id(
        env,
        ["edi_exchange_deduplicate_oca.cron_edi_backend_delete_obsolete_records"],
    )
