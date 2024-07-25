This module adds options for deduplication records before sending step on type:
    - deduplicate_on_send: check if a fresher one does not exist for the same record. If so, mark the oldest one as obsolete.
    - delete_obsolete_records: Delete records marked as obsolete.
