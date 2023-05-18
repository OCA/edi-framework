Get / set metadata
~~~~~~~~~~~~~~~~~~

On a `edi.exchange.record`:

    exc_record.set_metadata({...})
    exc_record.get_metadata()


Automatically store metadata from consumer records
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Make sure your model inherits from `edi.exchange.consumer.mixin`
* Override `_edi_get_metadata_to_store`

NOTE: automatic storage happens only when `create` gets called in an EDI framework session (`edi_framework_action` is in ctx).
