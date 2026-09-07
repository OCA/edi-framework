# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import PartyHelperCommonTestCase

# Business logic is tested against `EDIParty` directly in
# `test_party_helper.py`. This suite only exercises the `edi.party.helper`
# abstract model wiring on top of it.


class PartyHelperModelTestCase(PartyHelperCommonTestCase):
    def _get_party(self, partner, **kw):
        return self.env["edi.party.helper"].get_party(self.exc_record, partner, **kw)

    def test_data(self):
        expected = self._make_expected_data(self.partner1, 1)
        party = self._get_party(self.partner1)
        self.assertEqual(party, expected)

    def test_data_name_field_override(self):
        expected = self._make_expected_data(self.partner1, 1, name_field="display_name")
        party = self._get_party(self.partner1, name_field="display_name")
        self.assertEqual(party, expected)

    def test_data_limited(self):
        self.exc_type.id_category_ids = self.category2
        expected = self._make_expected_data(self.partner2, 2, allowed_codes=["cat2"])
        party = self._get_party(self.partner2)
        self.assertEqual(party, expected)
