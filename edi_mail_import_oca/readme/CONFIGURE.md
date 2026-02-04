For handling this incoming data, you just need to create a Backend and define the alias.

The alias will be used to detect input mails.
If the system detects an email, it will take all the exchange types related to the backend and review by exchange_filename if the pattern is filled.
It will create a new exchange record for each exchange type that fulfills:

1. Has the same backend type id
2. Has no backend or the backend is the current one
3. Has mail `Mail Record Policy` is `full` (it will generate a JSON file with the full email) or the policy is `pattern` and there is a file that follows the pattern (it will be used as the file for the exchange record)

If not exchange type can be found, a UserError and a bounce email are sent.

Processing will be handled in the standard way.
