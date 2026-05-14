Introduce a new system for **global EDI events** based on ``edi.configuration``
that can replace the use of component events.

Any ``edi.configuration`` flagged as ``is_global`` is now picked up by
``EDIExchangeRecord._trigger_edi_event`` and its ``snippet_do`` is executed
whenever the matching event fires (``done``, ``error``, ``ack_received``,
``ack_missing``, ``ack_received_error``, ``<action>_complete``, ...).

Filtering is performed via the new ``edi.configuration.edi_get_conf_global``
model method, which selects active global configurations matching the event
trigger code and, when set, the exchange type, the backend and the related
record model carried by the exchange record (empty values still mean "applies
to all"). This lets integrators subscribe to EDI events declaratively from
the UI instead of writing component listeners.

Full test coverage is included for the dispatch on all ``notify_*`` events
(both on the exchange record and on the related record target) and for the
new filtering rules.

Last but not lease: add minimal docs for edi.configuration.
