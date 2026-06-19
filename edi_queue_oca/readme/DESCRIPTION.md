This module integrates EDI with Queue Job and now the edi exchange records are generated using queue.

No need of doing a configuration on it, however, we can specify priority and channel in exchange type.

Exchange types can also define a daily execution time with `eta_time`.
The value is entered as a `float_time` in the current user's timezone
(`22.5` means 22:30 local time) and is converted at runtime to the next
matching UTC datetime used as the queue job ETA.
