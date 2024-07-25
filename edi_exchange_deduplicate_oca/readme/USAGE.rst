
With all the types that have been enabled "Deduplicate on Send" option, this module will check their records if a fresher one does not exist for the same record. If so, mark the oldest one as obsolete (except "block_obsolescence" records)
  - "block_obsolescence" is an technical option on records to avoid marking them as obsolete.

With all the types that have been enabled "Delete obsolete records" option, the cron will remove their obsolete records.
  - If the records are obsolete, delete them even if their type's flag has been disabled.
