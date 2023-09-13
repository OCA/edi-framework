# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.edi_oca.tests.common import EDIBackendCommonComponentTestCase
from odoo.addons.edi_party_data_oca.utils import get_party_data_component


class PartyDataTestCaseEDIFACT(EDIBackendCommonComponentTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend_edifact = cls.env.ref("edi_edifact_oca.edi_backend_edifact_demo")
        cls.backend_no_edifact = cls.env.ref("edi_oca.demo_edi_backend")
        cls.exc_type = cls._create_exchange_type(
            name="EDIFACT output test",
            code="edifact_out_test",
            direction="output",
            backend_id=cls.backend_edifact.id,
            backend_type_id=cls.backend_edifact.backend_type_id.id,
        )
        cls.exc_record_edifact = cls.backend_edifact.create_record(
            "edifact_out_test", {}
        )
        cls.partner = cls.env["res.partner"].create({"name": "EDIFACT Test"})

    def test_lookup_edifact(self):
        provider = get_party_data_component(self.exc_record_edifact, self.partner)
        self.assertEqual(provider._name, "edi.party.data.edifact")
        self.assertEqual(provider.partner, self.partner)
        self.assertFalse(provider.allowed_id_categories)
