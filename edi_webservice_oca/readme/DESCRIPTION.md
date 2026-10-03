**Deprecated as a direct dependency.** This module is now just an umbrella
kept to preserve existing installations: it depends on both
`edi_webservice_core_oca` (the `webservice.backend` link on `edi.backend`,
no `component` dependency) and `edi_webservice_component_oca` (the
deprecated `component`-based send integration), both of which used to be
part of this module. A warning is logged on startup as a reminder.

New code should depend on `edi_webservice_core_oca` directly, and
additionally on `edi_webservice_component_oca` only if it actually uses
the `component`-based `edi.webservice.send` integration.
