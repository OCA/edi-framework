No configuration is required: on installation every exchange type
stores the content of its files in the database.

To change it for one exchange type:

1.  Go to *EDI \> Config \> Exchange types* and open the type.
2.  Untick **Store File Content in Database** to keep the content of its
    files in the filestore, or set **Max File Content Size in Database
    (KB)** so that bigger files keep their content in the filestore. 0
    uses the global limit.

To set the global limit, go to *Settings \> Technical \> Parameters \>
System Parameters* (developer mode) and edit
`edi_exchange_file_db_oca.max_size_kb`, in KB. The module creates it
with `0`, which means no limit.

Both settings apply when a file is written: the files already stored
keep their content where it is (see **Usage**).
