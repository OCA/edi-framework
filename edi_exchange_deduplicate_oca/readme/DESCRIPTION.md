This module adds options for deduplication of exchange records on the exchange type:

- deduplicate_on_exchange: when a record is created, check if older records for
  the same record are still pending. If so, mark them as obsolete, so only the
  freshest one is sent or processed. Records without a related record match on
  the exchange type alone, which suits full-dump payloads where only the latest
  one matters.
- delete_obsolete_records: Delete records marked as obsolete.
