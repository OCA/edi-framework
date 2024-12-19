# Copyright 2024 Camptocamp
# Copyright 2024 Dixmit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """
    We just move the data to a new column.
    Data will be moved on post-migration
    """
    openupgrade.rename_columns(env.cr, {"edi_backend": [("storage_id", None)]})
