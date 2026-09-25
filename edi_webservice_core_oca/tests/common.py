# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64

from odoo.addons.edi_core_oca.tests.common import EDIBackendCommonTestCase


class TestEDIWebserviceCoreBase(EDIBackendCommonTestCase):
    @classmethod
    def _get_backend(cls):
        return cls.env.ref("edi_webservice_core_oca.demo_edi_backend")

    @classmethod
    def _setup_records(cls):
        result = super()._setup_records()
        cls.filedata = base64.b64encode(b"This is a simple file")
        vals = {
            "model": cls.partner._name,
            "res_id": cls.partner.id,
            "exchange_file": cls.filedata,
        }
        cls.record = cls.backend.create_record("test_csv_output", vals)
        cls.record.type_id.send_model_id = cls.env.ref(
            "edi_webservice_core_oca.model_edi_webservice_send"
        )
        return result
