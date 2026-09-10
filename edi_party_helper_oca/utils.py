# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections.abc import MutableMapping
from dataclasses import dataclass

from odoo.tools import DotDict


@dataclass(eq=False)
class EDIParty(MutableMapping):
    """Party information for an EDI exchange.

    The instance itself *is* the party: `name`, `identifiers`, `endpoint`
    and `lang` are computed on init and exposed as plain attributes,
    alongside `partner`. It also behaves like a mutable mapping of those
    (eg: ``party["name"]``, ``dict(party)``, equality against a plain dict)
    for backward compatibility with code expecting the old
    ``DotDict``-based party data.

    `name_field` and `lang_code` are constructor-only overrides for their
    respective computed attributes (`name`, `lang`). `endpoint` is derived
    from the exchange type's `endpoint_partner_category_id` (an id_number in
    that category, rendered with its `scheme`/`code`) when set. To force a
    different value, use ``party["endpoint"] = ...`` or
    ``party.update(endpoint=...)`` rather than plain attribute assignment
    (``party.endpoint = ...``) - the latter is a forbidden opcode
    (`STORE_ATTR`) under `safe_eval`, so it doesn't work from a restricted
    context like an `edi.exchange.template.output` `code_snippet`; item
    assignment (`STORE_SUBSCR`) does, and is exactly what `safe_eval`
    reserves for this (see its own comment on why `STORE_ATTR` is blocked).
    """

    exchange_record: object
    partner: object
    name_field: str = "name"
    lang_code: str | bool = False
    #: constructor/config attributes, not part of the party data itself:
    #: excluded from the Mapping interface (dict-like access / equality).
    _non_party_attrs = frozenset(
        {
            "exchange_record",
            "name_field",
            "lang_code",
            "allowed_id_categories",
        }
    )

    def __post_init__(self):
        self.allowed_id_categories = self.exchange_record.type_id.id_category_ids
        # NB: for UBL this should probably replace
        # `base.ubl._ubl_get_party_identification` which does nothing today.
        self.name = self._get_name()
        self.identifiers = self._get_identifiers()
        self.endpoint = self._get_endpoint()
        self.lang = self._get_lang()

    @property
    def env(self):
        return self.exchange_record.env

    def _party_data_keys(self):
        return [k for k in vars(self) if k not in self._non_party_attrs]

    def __getitem__(self, key):
        if key in self._non_party_attrs or key not in vars(self):
            raise KeyError(key)
        return getattr(self, key)

    def __setitem__(self, key, value):
        if key in self._non_party_attrs:
            raise KeyError(key)
        setattr(self, key, value)

    def __delitem__(self, key):
        raise TypeError(f"{type(self).__name__} does not support item deletion")

    def __iter__(self):
        return iter(self._party_data_keys())

    def __len__(self):
        return len(self._party_data_keys())

    def _get_name(self):
        return self.partner[self.name_field]

    def _get_endpoint(self):
        category = self.exchange_record.type_id.endpoint_partner_category_id
        if not category:
            return {}
        id_number = self.partner.id_numbers.filtered(
            lambda x: x.category_id == category
        )[:1]
        return self._get_identity(id_number) if id_number else {}

    def _get_identifiers(self):
        identifiers = self.partner.id_numbers.filtered(
            lambda x: self._filter_id_number(x)
        )
        return [self._get_identity(x) for x in identifiers]

    def _filter_id_number(self, id_number):
        if self.allowed_id_categories:
            return id_number.category_id in self.allowed_id_categories
        return True

    def _get_identity(self, id_number):
        category = id_number.category_id
        return DotDict(
            attrs={
                "schemeID": category.scheme or category.code,
            },
            value=id_number.name,
        )

    def _get_lang(self):
        lang_code = self.lang_code or self.partner.lang
        if not lang_code:
            return False
        lang = self.env["res.lang"]._get_data(code=lang_code)
        if not lang:
            return False
        return DotDict(
            {"name": lang.name, "code": lang.code, "short": lang.code.split("_")[0]}
        )
