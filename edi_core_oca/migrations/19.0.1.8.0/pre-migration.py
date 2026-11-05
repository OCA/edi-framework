# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Old records are now archived and deleted by the base autovacuum cron
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "edi_core_oca.ir_cron_archive_old_edi_records",
            "edi_core_oca.ir_cron_delete_old_archived_edi_records",
        ],
    )
