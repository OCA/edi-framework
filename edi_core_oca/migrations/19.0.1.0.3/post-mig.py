# Copyright 2026 Camptocamp SA (http://www.camptocamp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from logging import getLogger

from openupgradelib import openupgrade

_logger = getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    xmlid = "edi_core_oca.rule_edi_exchange_record_user"
    if rule := env.ref(xmlid, False):
        old_domain = (rule.domain_force or "").strip()
        new_domain = ["|", ("model", "!=", False), ("res_id", "=", 0)]
        _logger.info(
            f"Updating {rule} ({xmlid=}) domain:\n"
            f" - old: {old_domain}\n"
            f" - new: {new_domain}"
        )
        rule.domain_force = new_domain
    else:
        _logger.warning(f"No rule found with XMLID '{xmlid}', skipping...")
