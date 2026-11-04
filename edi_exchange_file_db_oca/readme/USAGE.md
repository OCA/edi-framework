Exchange files are handled as before: the module only changes where
their content is kept.

To read the content of an exchange file:

1.  Go to *EDI \> Exchanges* and open an exchange record.
2.  Open the **File Content** tab. JSON is indented, and JSON and XML
    are highlighted; other text, such as CSV or EDIFACT, is shown as it
    is. Text that does not match the encoding of the exchange type is
    decoded with the encoding detected from its content.

Binary files, such as PDF, images or spreadsheets, and files above
1 MB are not displayed: the tab shows their type, or their size limit,
and they are downloaded from the **Exchange file** field.

On installation, the content of the existing exchange files is moved
from the filestore to the database, following the type settings. Files
missing from the filestore, or whose content does not match their
checksum, are left untouched. The server log reports how many files
were moved and skipped. The moved filestore files are deleted by the
regular filestore garbage collection.

To move the existing files again later, for instance after enabling a
type or raising its limit, run from an Odoo shell:

``` python
from odoo.addons.edi_exchange_file_db_oca.hooks import (
    move_exchange_file_contents_to_db,
)

move_exchange_file_contents_to_db(env)
env.cr.commit()
```

Uninstalling the module keeps every file readable, since Odoo reads the
content of an attachment from the database or from the filestore,
wherever it is; new files go to the filestore again. To move the stored
content back to the filestore as well, run
`env["ir.attachment"].force_storage()` with the system parameter
`ir_attachment.location` set to `file`.
