Glue between `edi_payload_tracking_oca` and `edi_queue_oca`, installed
automatically with both.

When a job stores the payload of a record whose payload was just created by
a concurrent job, the job is retried instead of failing.
