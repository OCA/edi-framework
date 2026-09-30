Glue module between `edi_exchange_deduplicate_oca` and `edi_queue_oca`.

When an exchange record becomes obsolete, its jobs that have not started yet
are cancelled, so that superseded records are not generated, sent or processed.
