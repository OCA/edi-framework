Some partners (e.g. warehouse management systems) expect updates to contain
only what changed since the last export. To build such an update, the sender
needs to know what it already sent for each record. Each integration used to
store this on its own. This module stores it once, for any model.
