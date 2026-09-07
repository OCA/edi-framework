Via the `edi.party.helper` abstract model:

    party = self.env["edi.party.helper"].get_party(exchange_record, partner)

Or directly, with no ORM registry lookup involved:

    from odoo.addons.edi_party_helper_oca.utils import EDIParty

    party = EDIParty(exchange_record=exchange_record, partner=partner)

Both return an `EDIParty` instance: the party data (`name`, `identifiers`,
`endpoint`, `lang`) is exposed directly as attributes, alongside `partner`.
It also behaves like a read-only dict of those same keys (`party["name"]`,
`dict(party)`, equality against a plain dict), for backward compatibility
with code expecting the old `DotDict`-based party data.

Both accept the same optional keyword arguments: `name_field` (defaults to
`"name"`) and `lang_code` (a language code overriding the partner's own).
