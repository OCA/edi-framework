Base EDI backend.

Provides following models:

1.  EDI Backend, to centralize configuration
2.  EDI Backend Type, to classify EDI backends (eg: UBL, GS1, e-invoice,
    pick-yours)
3.  EDI Exchange Type, to define file types of exchange
4.  EDI Exchange Record, to define a record exchanged between systems

Also define a mixin to be inherited by records that will generate EDIs.

In addition, the module ships an ``edi.configuration`` mechanism that lets
users react to EDI events declaratively, by writing small Python snippets
attached to event triggers. This can be used as a lightweight alternative
to component event listeners: configurations can react globally (on any
exchange) or be scoped to a specific partner (or any related record),
exchange type, backend and target model. See ``CONFIGURE.md`` for details.
