# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.is_module_installed(env.cr, "edi_account_core_oca"):
        return
    openupgrade.update_module_names(
        env.cr, [("edi_account_core_oca", "edi_account_oca")], merge_modules=True
    )
