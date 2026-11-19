Glue between `edi_exchange_deduplicate_oca` and `edi_payload_tracking_oca`.

It adds the *Deduplicate unchanged payloads* option to output exchange types:
an exchange whose payload holds nothing new compared with the payload already
exported for its record is not sent, and is marked as obsolete instead. The
payload of a record deleted meanwhile is not sent either.
