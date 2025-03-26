# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.component.core import Component
from odoo.addons.edi_storage_core_oca.abstracts.receive import EDIStorageReceive


class EDIStorageReceiveComponent(EDIStorageReceive, Component):
    _name = "edi.storage.component.receive"
    _inherit = [
        "edi.component.receive.mixin",
        "edi.storage.component.mixin",
    ]
    _usage = "storage.receive"

    def receive(self):
        return self._receive(self.exchange_record)
