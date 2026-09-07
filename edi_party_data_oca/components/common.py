# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class EDIExchangePartyDataMixin(AbstractComponent):
    """Abstract component mixin provide partner data for exchanges.

    .. deprecated::
        Business logic lives in the `edi_party_helper_oca` module, which has
        no component dependency: `EDIParty` (plain dataclass) or the
        `edi.party.helper` abstract model. This component only wraps it for
        backward compatibility and will be dropped once its usages are
        ported over.
    """

    _name = "edi.party.data.mixin"
    _inherit = "edi.component.mixin"
    _collection = "edi.backend"
    _usage = "edi.party.data"

    def __init__(self, work_context):
        super().__init__(work_context)
        self.partner = self._get_partner()
        self.allowed_id_categories = self.exchange_record.type_id.id_category_ids

    def _get_partner(self):
        # Hook here to define different logic to lookup for the partner
        # based on current partner (eg: pick the parent).
        return self.work.partner

    def _get_party(self):
        return self.env["edi.party.helper"].get_party(
            self.exchange_record,
            self.partner,
            name_field=getattr(self.work, "party_data_name_field", "name"),
            lang_code=getattr(self.work, "lang", False),
        )

    def get_party(self):
        """Return party information.

        Requires a res.partner to be passed via work context.

        :return: `EDIParty` (behaves like a read-only dict too, for
            backward compatibility with the old ``DotDict``-based return)
        """
        return self._get_party()
