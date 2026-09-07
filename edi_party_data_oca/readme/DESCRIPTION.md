Technical module for the EDI suite module to retrieve data for parties
of an exchange.

This module provides default component and a mixin to be used for
registering new components for specific backends.

**Deprecated**: the actual party data lookup logic has moved to
`edi_party_helper_oca`, which has no dependency on the `component`
framework. This module now only wraps it in a component for backward
compatibility and will be removed once its usages are ported over. A
deprecation notice is logged on server startup while this module is
installed.
