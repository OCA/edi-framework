Technical module keeping, for each record, the payload last exported to a
third party through EDI.

It provides:

- `edi.payload.output`: one stored payload (JSON) per record, whatever its
  model;
- `edi.payload.consumer.mixin`: a mixin giving records direct access to their
  stored payload.

It has no functional effect on its own. Modules exporting data can use it to
send only what changed since the last export.
