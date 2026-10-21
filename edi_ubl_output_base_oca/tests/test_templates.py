# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo.tests.common import TransactionCase
from odoo.tools import DotDict

NS = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


class TestUblOutputBaseTemplates(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "ACME Vendor",
                "street": "Foo street 1",
                "street2": "Suite 2",
                "city": "Lausanne",
                "zip": "1000",
                "country_id": cls.env.ref("base.ch").id,
            }
        )

    def _render(self, template, values):
        return self.env["ir.qweb"]._render(template, values)

    def test_party_minimal(self):
        party = DotDict(name="ACME Vendor", identifiers=[], endpoint={})
        xml = self._render(
            "edi_ubl_output_base_oca.qweb_tmpl_ubl_party", {"party": party}
        )
        root = etree.fromstring(
            f"<root xmlns:cac='{NS['cac']}' xmlns:cbc='{NS['cbc']}'>{xml}</root>"
        )
        self.assertIsNone(root.find(".//cbc:EndpointID", NS))
        self.assertIsNone(root.find(".//cac:PartyIdentification", NS))
        self.assertEqual(root.find(".//cac:PartyName/cbc:Name", NS).text, "ACME Vendor")

    def test_party_with_endpoint_and_identifiers(self):
        party = DotDict(
            name="ACME Vendor",
            identifiers=[
                DotDict(attrs={"schemeID": "0088"}, value="8591234567894"),
            ],
            endpoint=DotDict(attrs={"schemeID": "0088"}, value="8591234567894"),
        )
        xml = self._render(
            "edi_ubl_output_base_oca.qweb_tmpl_ubl_party", {"party": party}
        )
        root = etree.fromstring(
            f"<root xmlns:cac='{NS['cac']}' xmlns:cbc='{NS['cbc']}'>{xml}</root>"
        )
        endpoint = root.find(".//cbc:EndpointID", NS)
        self.assertEqual(endpoint.text, "8591234567894")
        self.assertEqual(endpoint.get("schemeID"), "0088")
        identification = root.find(".//cac:PartyIdentification/cbc:ID", NS)
        self.assertEqual(identification.text, "8591234567894")

    def test_party_full_blocks(self):
        self.partner.write({"vat": "CHE-000.000.000 MWST", "phone": "+41 123434343"})
        party = DotDict(
            name="ACME Vendor",
            identifiers=[],
            endpoint={},
            partner=self.partner,
            lang={"name": "Schweiz / Deutsch", "code": "de_CH", "short": "de"},
        )
        xml = self._render(
            "edi_ubl_output_base_oca.qweb_tmpl_ubl_party",
            {
                "party": party,
                "show_full_address": True,
                "show_tax_scheme": True,
                "show_legal_entity": True,
                "show_contact": True,
            },
        )
        root = etree.fromstring(
            f"<root xmlns:cac='{NS['cac']}' xmlns:cbc='{NS['cbc']}'>{xml}</root>"
        )
        lang_node = root.find(".//cac:Language", NS)
        self.assertEqual(lang_node.find("cbc:ID", NS).text, "de")
        self.assertEqual(lang_node.find("cbc:Name", NS).text, "Schweiz / Deutsch")
        self.assertEqual(lang_node.find("cbc:LocaleCode", NS).text, "de_CH")
        self.assertEqual(
            root.find("cac:Party/cac:PostalAddress/cbc:StreetName", NS).text,
            "Foo street 1",
        )
        self.assertEqual(
            root.find(".//cac:PartyTaxScheme/cbc:CompanyID", NS).text,
            "CHE-000.000.000 MWST",
        )
        legal_entity = root.find(".//cac:PartyLegalEntity", NS)
        self.assertEqual(
            legal_entity.find("cbc:RegistrationName", NS).text, "ACME Vendor"
        )
        self.assertEqual(
            legal_entity.find("cac:RegistrationAddress/cbc:StreetName", NS).text,
            "Foo street 1",
        )
        contact = root.find(".//cac:Contact", NS)
        self.assertEqual(contact.find("cbc:Name", NS).text, "ACME Vendor")
        self.assertEqual(contact.find("cbc:Telephone", NS).text, "+41 123434343")

    def test_party_show_flags_default_off(self):
        # Without explicitly passing the `show_*` flags, none of the optional
        # blocks render, even when `party.partner` carries data for them.
        self.partner.write({"vat": "CHE-000.000.000 MWST"})
        party = DotDict(
            name="ACME Vendor", identifiers=[], endpoint={}, partner=self.partner
        )
        xml = self._render(
            "edi_ubl_output_base_oca.qweb_tmpl_ubl_party", {"party": party}
        )
        root = etree.fromstring(
            f"<root xmlns:cac='{NS['cac']}' xmlns:cbc='{NS['cbc']}'>{xml}</root>"
        )
        self.assertIsNone(root.find(".//cac:PostalAddress", NS))
        self.assertIsNone(root.find(".//cac:PartyTaxScheme", NS))
        self.assertIsNone(root.find(".//cac:PartyLegalEntity", NS))
        self.assertIsNone(root.find(".//cac:Contact", NS))

    def test_party_explicit_partner_overrides_party_partner(self):
        other_partner = self.env["res.partner"].create(
            {"name": "Other Partner", "street": "Other street"}
        )
        party = DotDict(
            name="ACME Vendor", identifiers=[], endpoint={}, partner=self.partner
        )
        xml = self._render(
            "edi_ubl_output_base_oca.qweb_tmpl_ubl_party",
            {"party": party, "partner": other_partner, "show_full_address": True},
        )
        root = etree.fromstring(
            f"<root xmlns:cac='{NS['cac']}' xmlns:cbc='{NS['cbc']}'>{xml}</root>"
        )
        self.assertEqual(
            root.find(".//cac:PostalAddress/cbc:StreetName", NS).text, "Other street"
        )

    def test_address(self):
        xml = self._render(
            "edi_ubl_output_base_oca.qweb_tmpl_ubl_address", {"partner": self.partner}
        )
        root = etree.fromstring(
            f"<root xmlns:cac='{NS['cac']}' xmlns:cbc='{NS['cbc']}'>{xml}</root>"
        )
        self.assertEqual(root.find("cbc:StreetName", NS).text, "Foo street 1")
        self.assertEqual(root.find("cbc:CityName", NS).text, "Lausanne")
        self.assertEqual(root.find("cbc:PostalZone", NS).text, "1000")
        self.assertEqual(root.find("cac:AddressLine/cbc:Line", NS).text, "Suite 2")
        self.assertEqual(root.find("cac:Country/cbc:IdentificationCode", NS).text, "CH")
