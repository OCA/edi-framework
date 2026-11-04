The gate is applied in a single override of
`edi.exchange.record._notify_related_record`, which `edi_oca` calls with
an `action` argument naming the exchange action the note comes from
(`generate`, `send`, `process`, `receive`), or `None` when the note is
not bound to one.

`edi.exchange.type._notify_related_record_on(action)` resolves the
matching `notify_related_record_on_<action>` field and returns `True`
when no such field exists. So supporting a new action is only a matter
of adding a field with that name — no change to the gate itself.

The `process` action is the one reached from two different places, which
is why it is the only toggle not restricted by direction. An input record
is processed by `edi_backend.exchange_process`, which is input-only.
An output record never goes through it: it is instead polled by the
`check` component resolved in `edi_backend._exchange_output_check_state`,
which reports back whether the other party processed the file. Both end
up calling `_notify_done` / `_notify_error`, hence the shared toggle.

Note that this second path is not tied to any particular backend: the
component is resolved generically, so a storage, webservice or custom
backend providing its own `check` component all behave the same way.
