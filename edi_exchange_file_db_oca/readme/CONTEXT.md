Databases are often restored without their filestore for development,
debugging or testing: on a busy instance it can weigh far more than the
database, and copying it makes every restore slower and heavier. Such a
database keeps every exchange record but none of their files, so an
exchange can no longer be inspected, reprocessed or replayed to
reproduce an issue. EDI payloads are usually small and a negligible
share of the filestore, so keeping their content in the database costs
little.
