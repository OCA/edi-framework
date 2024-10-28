## Get / set metadata

On a \`edi.exchange.record\`:

> exc\_record.set\_metadata({...}) exc\_record.get\_metadata()

## Automatically store metadata from consumer records

  - Make sure your model inherits from edi.exchange.consumer.mixin
  - Override \_edi\_get\_metadata\_to\_store

NOTE: automatic storage happens only when create gets called in an EDI
framework session (edi\_framework\_action is in ctx).
