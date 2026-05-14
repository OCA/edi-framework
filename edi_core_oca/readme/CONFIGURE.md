This module aims to provide an infrastructure to simplify
interchangability of documents between systems providing a configuration
platform. It will be inherited by other modules in order to define the
proper implementations of components.

In order to define a new Exchange Record, we need to configure:

- Backend Type
- Exchange Type
- Backend
- Components

## Jobs

- **Internal User**: might be an EDI user without even knowing about it, triggering EDI flows by some of his actions on business records; does not need access to related queue jobs.

- **EDI User**: more conscious EDI user that might sometimes need to debug things a bit further and thus needs access to related queue jobs.

- **EDI Manager**: full configuration access.

## Code to execute

By default, EDI Framework uses fields on `edi.backend` to get the right function to execute.
Each function is related to a model where the specific function is defined.
This models needs to inherit the specific handler of each case.

- receive: model `edi.oca.handler.receive` with function receive.
- process: model `edi.oca.handler.process` with function process.
- generate: model `edi.oca.handler.generate` with function generate.
- send: model `edi.oca.handler.send` with function send.
- check: model `edi.oca.handler.check` with function check.
- validate on inputs: model `edi.oca.handler.input.validate` with function input_validate.
- validate on outputs: model `edi.oca.handler.output.validate` with function input_validate.

You can see an example on the tests fake_models.

For a more complex behaviour, you can use `edi_component_oca` module to use components.

## User EDI generation

On the exchange type, it might be possible to define a set of models, a
domain and a snippet of code. After defining this fields, we will
automatically see buttons on the view to generate the exchange records.
This configuration is useful to define a way of generation managed by
user.

## Exchange type rules configuration

Exchange types can be further configured with rules. You can use rules
to:

1.  make buttons automatically appear in forms
2.  define your own custom logic

Go to an exchange type and go to the tab "Model rules". There you can
add one or more rule, one per model. On each rule you can define a
domain or a snippet to activate it. In case of a "Form button" kind, if
the domain and/ the snippet is/are satisfied, a form btn will appear on
the top of the form. This button can be used by the end user to manually
generate an exchange. If there's more than a backend and the exchange
type has not a backend set, a wizard will appear asking to select a
backend to be used for the exchange.

In case of "Custom" kind, you'll have to define your own logic to do
something.

## Custom event handlers via `edi.configuration`

The framework can dispatch EDI lifecycle events to user-defined
configurations, providing a declarative alternative to component events.
Each `edi.configuration` record links a **trigger** (an
`edi.configuration.trigger` code) to a **snippet** (`snippet_do`) that is
executed every time the matching event fires on an exchange record.

Built-in events fired by `EDIExchangeRecord` include:

- `on_edi_exchange_done` — exchange processed successfully
- `on_edi_exchange_error` — exchange ended in error
- `on_edi_exchange_done_ack_received` — ACK file received
- `on_edi_exchange_done_ack_missing` — expected ACK not received
- `on_edi_exchange_done_ack_received_error` — ACK received with errors
- `on_edi_exchange_<action>_complete` — generic action completion (e.g.
  `generate_complete`, `send_complete`), fired once on the exchange
  record and once on its related record when present

The snippet receives at least two variables in its evaluation context:

- `conf` — the current `edi.configuration` record
- `record` — the target of the event (either the `edi.exchange.record`
  itself or its related business record)

Plus the standard `edi_exec_snippet_do` extras (`operation`,
`edi_action`, `old_value`, `vals`, ...).

Two complementary lookup modes are available, and they can be combined
freely on the same flow.

### Global event configurations

Use this mode when you want a configuration to react to events on **any
business record** that travels through EDI, with no per-partner setup.

Tick **Global Configuration** (`is_global`) on the `edi.configuration`.
When an event fires, the framework calls
`edi.configuration.edi_get_conf_global(exchange_record, trigger)` which
selects all active global configurations whose `trigger` matches the
event code, filtered by the originating exchange record:

- **Exchange type** (`type_id`): must match the exchange record's type,
  or be left empty to apply to every type
- **Backend** (`backend_id`): must match the exchange record's backend,
  or be left empty to apply to every backend
- **Model** (`model_id` / `model_name`): must match the related record
  model (e.g. `sale.order`, `account.move`), or be left empty to apply
  to every model

Empty values mean "applies to all". Inactive configurations and
non-global configurations are ignored. All matching configurations are
executed in sequence.

Typical use cases:

- Posting a generic chatter message on every exchange that ends in error
- Pushing a notification to an external system every time an ACK is
  received for a given backend
- Logging extra audit information for every exchange of a given type

### Partner-specific (relation-based) event configurations

Use this mode when the reaction must depend on the partner (or any
other related record) involved in the exchange.

In this case configurations are **not** marked as global. Instead, the
business record exposes an `edi_config_ids` relation (via
`edi.exchange.consumer.mixin._edi_config_field_relation`, which by
default returns `self.env["edi.configuration"]` and can be overridden,
for example to point at `self.partner_id.edi_config_ids`). When an
event fires on the business record (e.g. on create, on write,
on send-via-email/EDI), the framework calls
`edi_confs.edi_get_conf(trigger)` on that relation and runs the
matching snippets.

Compared with global configurations:

- **Discovery** comes from the record's own relation, not from a
  database-wide search; this is the right place to model "this partner
  wants this behaviour" rules
- **Filtering** is reduced to `trigger` and (optionally) `backend_id`,
  since the recordset is already narrowed by the relation
- The same `snippet_do` API applies, so a snippet can be reused
  verbatim between global and partner-specific configurations

Typical use cases:

- Sending a specific EDI flow only for a subset of partners
- Customising the document generation per customer (e.g. different
  email template, different transport)
- Switching between EDI and email delivery based on partner
  preferences

