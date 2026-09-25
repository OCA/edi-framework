# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

# xids to pass to the new module
MOVED_XMLIDS = [
    "access_webservice_backend_edi_manager",
    "edi_backend_view_form",
]


def pre_init_hook(env):
    """Reuse `edi_webservice_oca`'s pre-split records instead of duplicating them."""
    openupgrade.rename_xmlids(
        env.cr,
        [
            (f"edi_webservice_oca.{xmlid}", f"edi_webservice_core_oca.{xmlid}")
            for xmlid in MOVED_XMLIDS
        ],
    )
