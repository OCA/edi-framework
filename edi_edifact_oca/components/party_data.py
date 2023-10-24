# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class EDIPartyDataEDIFACT(Component):
    """Party data provider specific to EDIFACT."""

    _name = "edi.party.data.edifact"
    _inherit = "edi.party.data"
    # TODO @simahawk: is a component per backend type really needed?
    _backend_type = "edifact"
