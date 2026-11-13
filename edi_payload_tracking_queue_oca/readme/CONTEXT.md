Exports usually run as queue jobs. Two jobs exporting the same record for the
first time at the same moment both try to create its stored payload: the
second one hits the unique constraint. Retrying that job is enough: next
time, it finds the stored payload and merges its own on top of it.
