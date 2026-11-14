Tick *Deduplicate unchanged payloads* on the output exchange type. The model of
the exported records must inherit `edi.payload.consumer.mixin`, and the send
handler must store the exported payload after each successful send
(`record.edi_payload_set_output()`).

Before sending, the payload of the exchange (a JSON object) is compared with
the stored one through `record._edi_payload_has_changes(payload)`: by default,
it has changes when nothing was exported yet, or when a key holds a value
different from the stored one. Override this method to refine the comparison
for a model.

Records of models that do not track their payload are sent as usual.
