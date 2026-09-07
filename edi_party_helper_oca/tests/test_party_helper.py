# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ..utils import EDIParty
from .common import PartyHelperCommonTestCase


class PartyDataHelperTestCase(PartyHelperCommonTestCase):
    def _get_party(self, partner, **kw):
        return EDIParty(exchange_record=self.exc_record, partner=partner, **kw)

    def test_lookup(self):
        party = self._get_party(self.partner1)
        self.assertEqual(party.partner, self.partner1)
        self.assertFalse(party.allowed_id_categories)

    def test_data(self):
        expected = (
            (self.partner1, self._make_expected_data(self.partner1, 1)),
            (
                self.partner2,
                self._make_expected_data(
                    self.partner2, 2, allowed_codes=["cat2", "cat3"]
                ),
            ),
            (
                self.partner3,
                self._make_expected_data(self.partner3, 3, allowed_codes=["cat3"]),
            ),
        )
        for partner, expected_data in expected:
            party = self._get_party(partner)
            self.assertEqual(party, expected_data)

    def test_data_fullname_override(self):
        # `name` is the default `name_field` since it doesn't embed
        # multi-company/disambiguation suffixes the way `display_name` does;
        # `display_name` is still available by explicit override.
        expected = (
            (
                self.partner1,
                self._make_expected_data(self.partner1, 1, name_field="display_name"),
            ),
            (
                self.partner2,
                self._make_expected_data(
                    self.partner2,
                    2,
                    allowed_codes=["cat2", "cat3"],
                    name_field="display_name",
                ),
            ),
            (
                self.partner3,
                self._make_expected_data(
                    self.partner3, 3, allowed_codes=["cat3"], name_field="display_name"
                ),
            ),
        )
        for partner, expected_data in expected:
            party = self._get_party(partner, name_field="display_name")
            self.assertEqual(party, expected_data)

    def test_lang(self):
        # No lang set on the partner -> `lang` is falsy.
        self.partner1.lang = False
        party = self._get_party(self.partner1)
        self.assertFalse(party.lang)
        # Partner's own lang is used by default.
        self.partner1.lang = "en_US"
        party = self._get_party(self.partner1)
        self.assertEqual(
            party.lang,
            {"name": "English (US)", "code": "en_US", "short": "en"},
        )
        # Explicit `lang_code` takes precedence over the partner's own lang.
        self.partner2.lang = False
        party = self._get_party(self.partner2, lang_code="en_US")
        self.assertEqual(
            party.lang,
            {"name": "English (US)", "code": "en_US", "short": "en"},
        )

    def test_partner_in_party_data(self):
        party = self._get_party(self.partner1)
        self.assertEqual(party.partner, self.partner1)

    def test_mapping_access(self):
        # `EDIParty` behaves like a read-only dict too, for backward
        # compatibility with the old `DotDict`-based party data.
        party = self._get_party(self.partner1)
        self.assertEqual(party["name"], party.name)
        self.assertEqual(party["partner"], self.partner1)
        self.assertEqual(
            set(party.keys()), set(self._make_expected_data(self.partner1, 1))
        )
        self.assertEqual(dict(party), self._make_expected_data(self.partner1, 1))
        with self.assertRaises(KeyError):
            party["allowed_id_categories"]  # pylint: disable=pointless-statement

    def test_data_limited_1(self):
        self.exc_type.id_category_ids = self.category1
        expected = (
            (
                self.partner1,
                self._make_expected_data(self.partner1, 1, allowed_codes=["cat1"]),
            ),
            (self.partner2, self._make_expected_data(self.partner2, 2, identifiers=[])),
            (self.partner3, self._make_expected_data(self.partner3, 3, identifiers=[])),
        )
        for partner, expected_data in expected:
            party = self._get_party(partner)
            self.assertEqual(party, expected_data)

    def test_data_limited_2(self):
        self.exc_type.id_category_ids = self.category2
        expected = (
            (
                self.partner1,
                self._make_expected_data(self.partner1, 1, allowed_codes=["cat2"]),
            ),
            (
                self.partner2,
                self._make_expected_data(self.partner2, 2, allowed_codes=["cat2"]),
            ),
            (self.partner3, self._make_expected_data(self.partner3, 3, identifiers=[])),
        )
        for partner, expected_data in expected:
            party = self._get_party(partner)
            self.assertEqual(party, expected_data)

    def test_data_limited_3(self):
        self.exc_type.id_category_ids = self.category3
        expected = (
            (
                self.partner1,
                self._make_expected_data(self.partner1, 1, allowed_codes=["cat3"]),
            ),
            (
                self.partner2,
                self._make_expected_data(self.partner2, 2, allowed_codes=["cat3"]),
            ),
            (
                self.partner3,
                self._make_expected_data(self.partner3, 3, allowed_codes=["cat3"]),
            ),
        )
        for partner, expected_data in expected:
            party = self._get_party(partner)
            self.assertEqual(party, expected_data)
