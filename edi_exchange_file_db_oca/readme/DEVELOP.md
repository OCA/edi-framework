Odoo decides where an attachment keeps its content in
`ir.attachment._get_datas_related_values`, from `_storage()`, which knows
neither the attachment's model nor its field. The decision is therefore
taken by the exchange record: `edi.exchange.record` writes its
**Exchange file** under the `edi_exchange_file_content_in_db` context
key, for which `ir.attachment._storage()` returns `db`. Records are
grouped by decision and each group is written with the key set to
`True` or `False`, so a value inherited from the caller never applies.

The key is scoped to the writing of the file only:

- on creation, `_create` is overridden rather than `create`, so the key
  covers the insertion of the rows and of their attachments, but not the
  quick execution of the exchange that `edi_oca` runs right after;
- on update, `write` writes the other values first, then the file alone.

`edi.exchange.type._should_store_file_content_in_db(size)` is the single
decision point: it combines the type's toggle with its size limit (the
type's own one, otherwise the global system parameter).

Content written to the attachment without going through the field, such
as `ir.attachment.force_storage()`, follows the configured storage
instead.

`hooks.move_exchange_file_contents_to_db` moves the existing content. It
selects the candidates in SQL, by batches, and asks their exchange type.
It reads each file, checks it against the stored checksum, and writes
the content with a batched SQL update: the checksum, size, mimetype and
index of the attachment stay valid since the content does not change,
and going through the ORM would recompute them for every attachment.

The **File Content** tab decides between text and binary before
decoding: a file is binary when `guess_mimetype` recognises a binary
signature (PDF, images, Office documents, archives), or when its first
KB holds a NUL byte (except for UTF-16 and UTF-32 types). Decoding
success alone is not a reliable signal, since a type in `latin-1`, or
with the `replace` error handler, decodes any byte sequence. The display
limit is `_get_exchange_file_display_max_size()`.
