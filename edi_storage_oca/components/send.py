# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo.addons.component.core import Component
from odoo.addons.edi_storage_core_oca.abstracts.send import EDIStorageSend


class EDIStorageSendComponent(EDIStorageSend, Component):
    _name = "edi.storage.component.send"
    _inherit = [
        "edi.component.send.mixin",
        "edi.storage.component.mixin",
    ]
    _usage = "storage.send"

    def send(self):
        # If the file has been sent already, refresh its state
        # TODO: double check if this is useless
        # since the backend checks the state already
        checker = self.component(usage="storage.check")
        result = checker.check()
        if not result:
            # all good here
            return True
        return self._send(self.exchange_record)
