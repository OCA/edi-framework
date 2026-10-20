Every note `edi_core_oca` posts on the related records goes through
`edi.exchange.record._notify_state(key, message, level)`, which this
module overrides to apply the rules. `key` is the status
(`_exchange_status_messages` key) and matches the `code` of an
`edi.notification.trigger`.

- A status with no trigger is always notified. A module calling
  `notify_action_complete` with its own action (status `<action>_ok`)
  can add a trigger with that code to make it configurable.
- `_notify_related_record` posts the note directly, bypassing the rules.
  Call `_notify_state` instead.
- New exchange types get their default rule on creation. Types created
  before the module install get it from the install hook or the
  migration.
- A module declaring its own rules for its exchange types creates them
  with the `edi_notification_skip_default_rule` context key, so they do
  not get the default rule. In a data file, set it on the record of the
  exchange type, and declare the rules as records of their own:

  ``` xml
  <record
      id="exchange_type_x"
      model="edi.exchange.type"
      context="{'edi_notification_skip_default_rule': True}"
  >
      ...
  </record>
  <record id="exchange_type_x_rule" model="edi.notification.rule">
      <field name="name">Notes on related records</field>
      <field name="type_id" ref="exchange_type_x" />
      <field
          name="trigger_ids"
          eval="[Command.set([ref('edi_notification_oca.trigger_send_ok')])]"
      />
  </record>
  ```
