Go to "EDI -\> Config -\> Backends" and edit or create one. Find the tab
"Webservice" and add a webservice. On the webservice record you can
specify all the general parameters to connect to the service (see
`webservice_core` README for more details). On the webservice backend
you can configure one or more `webservice.endpoint` records (path, HTTP
method, ...).

On the exchange type you want to send through a webservice, go to the
"Execution handlers" tab, set "Sender" to "EDI WebService Send Handler",
then pick the "Endpoint" to call in the "Webservice settings" group that
appears - it drives both the URL (backend URL + endpoint path) and the
HTTP method.

Static headers and querystring params are best set directly on the
`webservice.endpoint` record itself (its "Headers" and "URL Params"
tabs) - prefer that over the exchange type's advanced settings below,
which are meant for one-off, per-exchange-type overrides rather than
the endpoint's own regular configuration.

If you still need extra call parameters beyond what the endpoint (and
its own headers/URL params) provide, you can add them via the exchange
type's advanced settings:

    execution_model:
      send:
        webservice:
          kwargs:
            headers:
              X-Custom-Header: foo
            url_params:
              foo: baz

If you want to send data as bytes you can use the option send_as_bytes
on the exchange type (same tab).
