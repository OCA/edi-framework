This module keeps the content of EDI exchange files in the database
instead of the filestore, so a database restored without its filestore
still holds every exchange payload. The **Exchange file** of an exchange
record is still an attachment: only the place where that attachment
keeps its content changes, from a filestore file to the database, so
everything that reads, writes or searches exchange files works as
before. It is enabled for every exchange type on installation, can be
disabled per type, and a size limit keeps big files in the filestore.
The exchange record form also shows the content of text files in a
**File Content** tab, with JSON indented.
