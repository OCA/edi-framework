This module is meant for developers. Inherit the mixin on the model to lock
and list the fields to lock:

``` python
class StockPicking(models.Model):
    _inherit = ["stock.picking", "edi.lock.output.consumer.mixin"]

    def _edi_lock_output_fields(self):
        return super()._edi_lock_output_fields() + ["partner_id", "scheduled_date"]
```

Then tick *Lock record on send* on the output exchange types that lock the
record. A change to a listed field of a record with a sent exchange of such a
type raises an error.

To lock on another condition, override `_edi_lock_output_is_locked()`. It is
called on all the records being changed and returns the locked ones. Add yours
to the result of `super()`, so that the records already sent stay locked:

``` python
    def _edi_lock_output_is_locked(self):
        return super()._edi_lock_output_is_locked() | self.filtered("is_frozen")
```

To change the error message, override `_edi_lock_output_message()`.

The lock is bypassed:

- by the users of the *Bypass EDI output lock* group;
- by code, with the `edi_lock_output_bypass` key in the context, e.g. when
  processing the partner's own updates.
