from openupgradelib import openupgrade


def pre_init_hook(env):
    # Update the module name in the database
    # This should happen only if we migrate from edi_oca to edi_core_oca
    env.cr.execute(
        """
        UPDATE ir_model_data
        SET module = 'edi_core_oca'
        WHERE module = 'edi_oca'
        """
    )
    openupgrade.rename_xmlids(
        env.cr,
        [
            (
                "edi_core_oca.access_queue_job_user",
                "edi_queue_oca.access_queue_job_user",
            ),
        ],
    )


def post_init_hook(env):
    if env["ir.module.module"].search(
        [
            ("name", "=", "edi_oca"),
            ("state", "in", ["installed", "to upgrade", "to install"]),
        ]
    ):
        for module in ["edi_core_oca", "edi_queue_oca", "edi_component_oca"]:
            for data in env["ir.model.data"].search([("module", "=", module)]):
                if not env["ir.model.data"].search_count(
                    [("module", "=", "edi_oca"), ("name", "=", data.name)]
                ):
                    data.copy({"module": "edi_oca", "noupdate": True}).name = data.name
