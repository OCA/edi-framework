# Copyright 2020 ACSONE SA
# @author Simone Orsi <simahawk@gmail.com>
# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import models


class EDIBackend(models.Model):
    _inherit = "edi.backend"

    _storage_actions = ("check", "send", "receive")

    def _get_component_usage_candidates(self, exchange_record, key):
        candidates = super()._get_component_usage_candidates(exchange_record, key)
        if not self.storage_id or key not in self._storage_actions:
            return candidates
        return [f"storage.{key}"] + candidates

    def _component_match_attrs(self, exchange_record, key):
        # Override to inject storage_type
        res = super()._component_match_attrs(exchange_record, key)
        if not self.storage_id or key not in self._storage_actions:
            return res
        res["storage_type"] = self.sudo().storage_id.protocol
        return res

    def _component_sort_key(self, component_class):
        res = super()._component_sort_key(component_class)
        # Override to give precedence by storage_type when needed.
        if not self.storage_id:
            return res
        return (1 if getattr(component_class, "_storage_type", False) else 0,) + res
