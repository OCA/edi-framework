This module is meant for developers. Inherit the mixin on the model whose
records are exported:

``` python
class ProductProduct(models.Model):
    _inherit = ["product.product", "edi.payload.consumer.mixin"]
```

Then, in the handlers of the exchange:

- `record.edi_payload_get_output()` returns the payload stored for the record,
  or an empty dict if nothing was exported yet;
- `record.edi_payload_set_output(payload)` replaces the stored payload.

When two transactions export the same record for the first time
concurrently, the second one fails on the unique constraint. With
`edi_queue_oca`, `edi_payload_tracking_queue_oca` is installed automatically
and turns this into a retry of the job, which then finds the payload stored
by the first one.
