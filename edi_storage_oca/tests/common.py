# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.addons.edi_storage_core_oca.tests.common import TestEDIStorageBase

FS_STORAGE_MOCK_PATH = "odoo.addons.edi_storage_core_oca.utils"


class TestEDIStorageBaseComponent(TestEDIStorageBase):
    @classmethod
    def _setup_records(cls):
        res = super()._setup_records()
        cls.checker = cls.backend._find_component(
            cls.partner._name,
            ["storage.check"],
            work_ctx={"exchange_record": cls.record},
        )
        cls.checker_input = cls.backend._find_component(
            cls.partner._name,
            ["storage.check"],
            work_ctx={"exchange_record": cls.record_input},
        )
        cls.sender = cls.backend._find_component(
            cls.partner._name,
            ["storage.send"],
            work_ctx={"exchange_record": cls.record},
        )
        return res

    def _file_fullpath(self, state, record=None, ack=False, fname=None, checker=None):
        record = record or self.record
        checker = checker or self.checker
        if not fname:
            fname = self._filename(record, ack=ack)
        if state == "error-report":
            # Exception as we read from the same path but w/ error suffix
            state = "error"
            fname += ".error"
        return checker._get_remote_file_path(state, filename=fname).as_posix()
