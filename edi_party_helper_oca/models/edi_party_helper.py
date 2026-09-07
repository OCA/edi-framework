# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models

from ..utils import EDIParty


class EDIPartyHelper(models.AbstractModel):
    """Provide partner data for exchanges, without any component dependency."""

    _name = "edi.party.helper"
    _description = "EDI Party Helper"

    def get_party(self, exchange_record, partner, **kw):
        """Return the party for `partner` on `exchange_record`.

        :param exchange_record: an `edi.exchange.record` record
        :param partner: a `res.partner` record
        :param kw: forwarded to `EDIParty` (eg. `name_field`, `lang_code`)
        :return: `EDIParty`
        """
        return EDIParty(exchange_record=exchange_record, partner=partner, **kw)
