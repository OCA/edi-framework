# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ..utils import get_party_data_component
from .common import PartyDataCommonTestCase

# Business logic is tested against the component-independent helper in
# `test_party_helper.py`. This suite only exercises the component wiring
# (work context plumbing, hooks) on top of it.


class PartyDataTestCase(PartyDataCommonTestCase):
    def _get_provider(self, partner, **kw):
        return get_party_data_component(self.exc_record, partner, **kw)

    def test_lookup(self):
        provider = self._get_provider(self.partner1)
        self.assertEqual(provider.partner, self.partner1)
        self.assertFalse(provider.allowed_id_categories)

    def test_data(self):
        expected = self._make_expected_data(self.partner1, 1)
        provider = self._get_provider(self.partner1)
        self.assertEqual(provider.get_party(), expected)

    def test_data_limited(self):
        self.exc_type.id_category_ids = self.category2
        expected = self._make_expected_data(self.partner2, 2, allowed_codes=["cat2"])
        provider = self._get_provider(self.partner2)
        self.assertEqual(provider.get_party(), expected)

    def test_data_name_field_override(self):
        # `party_data_name_field` on the work context is forwarded to the
        # party's `name_field`.
        expected = self._make_expected_data(self.partner1, 1, name_field="display_name")
        provider = self._get_provider(
            self.partner1, work_ctx={"party_data_name_field": "display_name"}
        )
        self.assertEqual(provider.get_party(), expected)

    def test_lang_override_via_work_ctx(self):
        # `lang` on the work context is forwarded to the party's `lang_code`.
        self.partner2.lang = False
        provider = self._get_provider(self.partner2, work_ctx={"lang": "en_US"})
        self.assertEqual(
            provider.get_party()["lang"],
            {"name": "English (US)", "code": "en_US", "short": "en"},
        )

    def test_partner_in_party_data(self):
        provider = self._get_provider(self.partner1)
        self.assertEqual(provider.get_party()["partner"], self.partner1)
