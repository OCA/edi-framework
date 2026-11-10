This module has two **inactive** global `edi.configuration` records
that move the input file across the storage directories on
`on_edi_exchange_done` / `on_edi_exchange_error`:

- *Storage: move input file, pending → done (fallback error → done)
- *Storage: move input file, pending → error

Before enabling them you **must** set `backend_id` on the record:
otherwise the global match runs against every backend in the database,
including non-storage ones.
