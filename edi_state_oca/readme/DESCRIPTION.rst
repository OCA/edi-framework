Technical module for the EDI suite to provide additional states for any records.

Example: a SO is generated via UBL file and you want to provide an ORDRSP with the right state on the order and on each line.

It provides 2 new models:

* EDI state workflow

    * groups states together
    * limit states to a specific model

* EDI state

    * describe the state of the record
