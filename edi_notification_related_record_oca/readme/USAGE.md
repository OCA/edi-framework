To change what an exchange type posts on its related records, go to
**EDI** > **Exchange types**, open the type, and use the **Related
Record Notifications** page. Untick the actions that should stay silent
and save.

The four toggles map one to one onto the exchange actions:

- **Notify related record on generate** — when the exchange data is
  generated. Output types only.
- **Notify related record on send** — when the exchange is sent. Output
  types only.
- **Notify related record on process** — when the exchange is processed,
  successfully or with errors. Available for both directions, because
  each one has its own counterpart: an incoming exchange is processed by
  Odoo, whereas for an outgoing one it is the receiving party that
  reports back having processed it. Both share this single toggle.
- **Notify related record on receive** — when the exchange is received.
  Input types only.

Unticking a toggle suppresses the note only. The exchange record still
advances normally, keeps its state and error information, and still
triggers its events, so any automation built on top of them is
unaffected.
