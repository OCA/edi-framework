Glue module betweeb edi_exchange_template and edi_party_data.

Exposes a get_party_data function to the rendering context of the
template. This way you can retrieve party data on the fly.

**Deprecated**: `edi_party_data_oca` (and this glue module) are superseded
by `edi_party_helper_oca`, which has no dependency on the `component`
framework. Use its `edi.party.helper` model (or the `EDIParty` class
directly) instead of the `get_party_data` render context shortcut. A
deprecation notice is logged on server startup while this module is
installed. It is also no longer auto-installed.
