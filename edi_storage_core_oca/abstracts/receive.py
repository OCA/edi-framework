# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


class EDIStorageReceive:
    def _receive(self, exchange_record):
        return self._get_remote_file(exchange_record, "pending", binary=True)
