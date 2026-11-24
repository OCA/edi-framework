# Copyright 2026 Dixmit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(
        env.cr,
        [
            (
                "edi_exchange_template_oca.edi_exchange_template_output_view_tree",
                "edi_exchange_template_oca.edi_exchange_template_output_view_list",
            ),
            (
                "edi_exchange_template_oca.act_open_edi_exchange_template_output_view_tree",
                "edi_exchange_template_oca.act_open_edi_exchange_template_output_view_list",
            ),
        ],
    )
