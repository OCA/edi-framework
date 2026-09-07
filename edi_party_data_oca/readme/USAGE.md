An handy util method is to retrive the component:

    from odoo.addons.edi_party_data_oca.utils import get_party_data_component

    component = get_party_data_component(exchange_record, partner)

    data = component.get_party()

**Deprecated**: prefer `edi_party_helper_oca`'s `edi.party.helper` model or
its `EDIParty` class directly, they don't require any component lookup.
