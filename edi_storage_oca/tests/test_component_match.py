# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.component.core import Component
from odoo.addons.edi_oca.tests.common import EDIBackendCommonComponentRegistryTestCase


class EDIBackendTestCase(EDIBackendCommonComponentRegistryTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._load_module_components(cls, "edi_storage_oca")

    @classmethod
    def _get_backend(cls):
        return cls.env.ref("edi_storage_oca.demo_edi_backend_storage")

    def test_component_match(self):
        """Lookup with special match method."""

        class SFTPCheck(Component):
            _name = "sftp.check"
            _inherit = "edi.storage.component.check"
            _usage = "storage.check"
            # _backend_type = "demo_backend"
            _storage_type = "sftp"

        class SFTPSend(Component):
            _name = "sftp.send"
            _inherit = "edi.storage.component.send"
            _usage = "storage.send"
            # _backend_type = "demo_backend"
            _storage_type = "sftp"

        class S3Check(Component):
            _name = "s3.check"
            _inherit = "edi.storage.component.check"
            _usage = "storage.check"
            # _exchange_type = "test_csv_output"
            _storage_type = "s3"

        class S3Send(Component):
            _name = "s3.send"
            _inherit = "edi.storage.component.send"
            _usage = "storage.send"
            # _exchange_type = "test_csv_output"
            _storage_type = "s3"

        self._build_components(SFTPCheck, SFTPSend, S3Check, S3Send)

        # Record not relevant for these tests
        work_ctx = {"exchange_record": self.env["edi.exchange.record"].browse()}

        component = self.backend._find_component(
            "res.partner",
            ["storage.check"],
            work_ctx=work_ctx,
            backend_type="demo_backend",
            exchange_type="test_csv_output",
            storage_type="s3",
        )
        self.assertEqual(component._name, S3Check._name)

        component = self.backend._find_component(
            "res.partner",
            ["storage.check"],
            work_ctx=work_ctx,
            backend_type="demo_backend",
            exchange_type="test_csv_output",
            storage_type="sftp",
        )
        self.assertEqual(component._name, SFTPCheck._name)

        component = self.backend._find_component(
            "res.partner",
            ["storage.send"],
            work_ctx=work_ctx,
            backend_type="demo_backend",
            exchange_type="test_csv_output",
            storage_type="sftp",
        )
        self.assertEqual(component._name, SFTPSend._name)

        component = self.backend._find_component(
            "res.partner",
            ["storage.send"],
            work_ctx=work_ctx,
            backend_type="demo_backend",
            exchange_type="test_csv_output",
            storage_type="s3",
        )
        self.assertEqual(component._name, S3Send._name)
