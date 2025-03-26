# Copyright 2020 ACSONE
# Copyright 2022 Camptocamp
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging

from odoo.addons.component.core import AbstractComponent
from odoo.addons.edi_storage_core_oca.abstracts.base import EDIStorageMixin

_logger = logging.getLogger(__file__)


class EDIStorageComponentMixin(EDIStorageMixin, AbstractComponent):
    _name = "edi.storage.component.mixin"
    _inherit = "edi.component.mixin"
    # Components having `_storage_type` will have precedence.
    # If the value is not set, generic components will be used.
    _storage_type = None

    @classmethod
    def _component_match(cls, work, usage=None, model_name=None, **kw):
        res = super()._component_match(work, usage=usage, model_name=model_name, **kw)
        storage_type = kw.get("storage_type")
        if storage_type and cls._storage_type:
            return cls._storage_type == storage_type
        return res

    @property
    def storage(self):
        return self.backend.storage_id

    def _dir_by_state(self, direction, state):
        """Return remote directory path by direction and state.

        :param direction: string stating direction of the exchange
        :param state: string stating state of the exchange
        :return: PurePath object
        """
        return self._get_dir_by_state(self.backend, direction, state)
