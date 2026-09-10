# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools import safe_eval

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

    def test_endpoint_manual_override(self):
        # No `endpoint_partner_category_id` -> `endpoint` falsy by default.
        party = self._get_party(self.partner1)
        self.assertFalse(party.endpoint)
        # `EDIParty` is a `MutableMapping`: item assignment and `.update()`
        # both work, and keep the `.endpoint` attribute in sync.
        endpoint = {"attrs": {"schemeID": "0088"}, "value": "7300070011115"}
        party["endpoint"] = endpoint
        self.assertEqual(party.endpoint, endpoint)
        party.update(endpoint={"attrs": {"schemeID": "0088"}, "value": "other"})
        self.assertEqual(
            party.endpoint, {"attrs": {"schemeID": "0088"}, "value": "other"}
        )
        # Item deletion isn't supported.
        with self.assertRaises(TypeError):
            del party["endpoint"]

    def test_endpoint_override_from_safe_eval(self):
        # This is the actual point of supporting item assignment: plain
        # attribute assignment (`party.endpoint = ...`) is a forbidden
        # opcode (`STORE_ATTR`) under `safe_eval` - e.g. from an
        # `edi.exchange.template.output` `code_snippet` - but item
        # assignment (`STORE_SUBSCR`) isn't, so `party['endpoint'] = ...`
        # works from there too.
        party = self._get_party(self.partner1)
        endpoint = {"attrs": {"schemeID": "0088"}, "value": "7300070011115"}
        safe_eval.safe_eval(
            "party['endpoint'] = endpoint",
            {"party": party, "endpoint": endpoint},
            mode="exec",
            nocopy=True,
        )
        self.assertEqual(party.endpoint, endpoint)
        with self.assertRaises(ValueError):
            safe_eval.safe_eval(
                "party.endpoint = endpoint",
                {"party": party, "endpoint": endpoint},
                mode="exec",
                nocopy=True,
            )

    def test_endpoint_from_category(self):
        # No `endpoint_partner_category_id` configured -> falsy, even though
        # the partner has matching id_numbers.
        party = self._get_party(self.partner1)
        self.assertFalse(party.endpoint)
        # Configured -> derived from that category's id_number, schemeID
        # falling back to `code` (no `scheme` set here).
        self.exc_type.endpoint_partner_category_id = self.category1
        party = self._get_party(self.partner1)
        self.assertEqual(
            party.endpoint,
            {"attrs": {"schemeID": "cat1"}, "value": "cat1-p1"},
        )
        # With `scheme` set on the category, it's used instead of `code`.
        self.category1.scheme = "0088"
        party = self._get_party(self.partner1)
        self.assertEqual(
            party.endpoint,
            {"attrs": {"schemeID": "0088"}, "value": "cat1-p1"},
        )
        # Partner has no id_number in the configured category -> falsy.
        self.exc_type.endpoint_partner_category_id = self.category1
        party = self._get_party(self.partner3)
        self.assertFalse(party.endpoint)

    def test_identifier_scheme_override(self):
        # No `scheme` set on the category -> schemeID falls back to `code`
        # (this is what cat1/cat2/cat3 already exercise in test_data).
        # With `scheme` set, it's used instead of `code`.
        self.category1.scheme = "0088"
        party = self._get_party(self.partner1)
        cat1_identifier = [i for i in party.identifiers if i.value == "cat1-p1"][0]
        self.assertEqual(cat1_identifier.attrs["schemeID"], "0088")

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
