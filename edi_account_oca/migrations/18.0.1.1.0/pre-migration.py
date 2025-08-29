from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # We recreate the ir.model.data records in the
    # edi_oca module to ensure that other modules work properly
    for module in ["edi_account_core_oca"]:
        for data in env["ir.model.data"].search([("module", "=", module)]):
            if not env["ir.model.data"].search_count(
                [("module", "=", "edi_account_oca"), ("name", "=", data.name)]
            ):
                data.copy(
                    {"module": "edi_account_oca", "noupdate": True}
                ).name = data.name
