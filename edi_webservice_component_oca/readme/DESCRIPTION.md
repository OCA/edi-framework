Provides the `component`-based `edi.webservice.send` integration for EDI
Exchange records (configured via an exchange type's advanced settings,
under `components: send: usage: webservice.send`), for setups that still
rely on it - including any custom `_inherit` of this component.

It used to be part of `edi_webservice_oca` itself; it now lives here so
that installing `edi_webservice_oca` no longer requires `component`
unless you actually need this integration style.

This module itself is not deprecated: it's the supported way to get
`component`-based integration on demand. The integration *style* is the
legacy one, though - new exchange types should use the model-based
handler in `edi_webservice_core_oca` instead (selected via
`send_model_id`).
