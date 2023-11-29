# Copyright 2023 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import yaml

from odoo import api, fields, models

from odoo.addons.base_sparse_field.models.fields import Serialized


class EDIExchangeTypeRule(models.Model):
    _inherit = "edi.exchange.type.rule"

    kind = fields.Selection(
        selection_add=([("auto", "Auto")]), ondelete={"auto": "set default"}
    )
    auto_conf = Serialized(default={}, compute="_compute_auto_conf")
    auto_conf_edit = fields.Text()

    @api.depends("auto_conf_edit")
    def _compute_auto_conf(self):
        for rec in self:
            rec.auto_conf = rec._load_auto_conf()

    def _load_auto_conf(self):
        # TODO: validate settings w/ a schema.
        # Could be done w/ Cerberus or JSON-schema.
        # This would help documenting core and custom keys.
        return yaml.safe_load(self.auto_conf_edit or "") or {}
