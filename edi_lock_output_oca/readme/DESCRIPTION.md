Technical module locking fields of records once their EDI output was sent,
so that what the partner received and what Odoo holds do not drift apart.

It provides:

- `edi.lock.output.consumer.mixin`: a mixin refusing changes to a list of
  fields of records that are locked;
- the *Lock record on send* option on output exchange types: by default, a
  record is locked once an exchange of such a type was sent for it;
- the *Bypass EDI output lock* group, whose users can still change locked
  fields.

It has no functional effect until a model uses the mixin.
