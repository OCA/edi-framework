With all the types that have been enabled "Deduplicate on Exchange" option, this module will check, when a record is created, if older records for the same record (or for the same type, when no record is linked) are still pending. If so, mark them as obsolete (except "block_obsolescence" records). An obsolete record is neither sent nor processed: its job does nothing.  
- "block_obsolescence" is an technical option on records to avoid
  marking them as obsolete.
- You can restrict deduplication to specific exchange states with the technical field "deduplicate_on_exchange_record_status" (comma-separated values from "edi_exchange_state").

With all the types that have been enabled "Delete obsolete records" option, the cron will remove their obsolete records.  
- If the records are obsolete, delete them even if their type's flag has
  been disabled.
