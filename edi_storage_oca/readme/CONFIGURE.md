This module has two **inactive** global `edi.configuration` records
that move the input file across the storage directories on
`on_edi_exchange_done` / `on_edi_exchange_error`:

- *Storage: move input file, pending → done (fallback error → done)
- *Storage: move input file, pending → error

Before enabling them you **must** set `backend_id` on the record:
otherwise the global match runs against every backend in the database,
including non-storage ones.

## Test environment

When `edi.backend.test_mode` is enabled (see `edi_core_oca`), the
backend resolves test-specific connection parameters through
`get_conn_parameter()` instead of the live ones:

- `test_storage_id` — an alternate `fs.storage` (different host,
  port, credentials), used when set
- `test_input_dir_*` / `test_output_dir_*` — alternate directories,
  each falling back to its live counterpart when empty

All file operations (polling, moves, sends, reads) go through
`get_conn_parameter()`, so enabling test mode never rewrites the
live configuration — flipping the checkbox back restores it
instantly. The *Test environment* group on the backend Storage page
only appears for backend types with test mode supported.

Connectors needing more test-switched parameters (URLs, credentials,
endpoints) extend `_edi_test_conn_param_fields()` and provide matching
`test_<name>` fields.
