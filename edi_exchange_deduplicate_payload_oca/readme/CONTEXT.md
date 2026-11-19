Integrations sending only what changed since the last export (see
`edi_payload_tracking_oca`) still include some keys in every payload, e.g. the
identifiers the partner needs. An export triggered by a change that does not
affect the payload then carries nothing new. Left pending, such an exchange
would be queued again by the output cron, forever: marking it as obsolete, as
`edi_exchange_deduplicate_oca` does for superseded exchanges, ends it.
