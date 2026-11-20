This module makes the notifications of exchange records configurable, per
exchange type, through notification rules.

A rule reacts to one or more exchange statuses (generated, sent, send
error, processed, process error, ACK missing, ...) and does one of the
following:

- **Note on related records**: posts the status note on the records the
  exchange is related to.
- **Activity on exchange record**: schedules an activity on the exchange
  record for the selected users and for the users of the selected groups
  (eg: on process errors).

Each exchange type gets a default *Notes on related records* rule with
every status, so installing the module changes nothing until the rules
are edited. Error notes are always posted on the related records.
