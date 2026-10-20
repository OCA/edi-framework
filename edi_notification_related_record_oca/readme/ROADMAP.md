This module is a stopgap. It may be deprecated in favour of a generic way
to configure every EDI notification (which note or activity, for which
exchange type and event, and for whom), such as a notification rule model
in `edi_notification_oca`. See the discussion in
<https://github.com/OCA/edi-framework/pull/317>.

Acknowledgement notes (`ack_received`, `ack_missing`,
`ack_received_error`) are not bound to a specific exchange action and
therefore have no toggle: they always post. Adding a dedicated one for
them would be a natural follow-up.
