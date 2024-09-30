# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

_model_renames = [
    ("edi.backend.group", "edi.exchange.type.group"),
]

_table_renames = [
    ("edi_backend_group", "edi_exchange_type_group"),
]

_xmlid_renames = [
    (
        "custom_module.access_edi_backend_group_manager",
        "custom_module.access_edi_exchange_type_group_manager",
    ),
    (
        "custom_module.access_edi_backend_group_user",
        "custom_module.access_edi_exchange_type_group_user",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.lift_constraints(env.cr, "edi_backend", "backend_group_id")
    openupgrade.remove_tables_fks(env.cr, "edi_backend_group")
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
