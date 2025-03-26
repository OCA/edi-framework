# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.component.core import Component
from odoo.addons.edi_storage_core_oca.abstracts.listener import (
    EdiStorageListenerAbstract,
)


class EdiStorageListener(EdiStorageListenerAbstract, Component):
    _name = "edi.storage.component.listener"
    _inherit = "base.event.listener"
