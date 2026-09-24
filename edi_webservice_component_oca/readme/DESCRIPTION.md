**Deprecated.** Provides the `component`-based `edi.webservice.send`
integration for EDI Exchange records (configured via an exchange type's
advanced settings, under `components: send: usage: webservice.send`),
kept only for backward compatibility with existing setups - including
any custom `_inherit` of this component.

It used to be part of `edi_webservice_oca` itself; it now lives here so
that installing `edi_webservice_oca` no longer requires `component`
unless you actually need this integration style.
