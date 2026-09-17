`edi_oca` posts a note on the chatter of an exchange record's related
records every time an exchange advances: on generate, send, receive and
process. This module makes each of those notes configurable per exchange
type, through four independent toggles on the exchange type form. All
four are enabled by default, so installing the module does not change
the behaviour of an existing database. Only the chatter note is
affected: the exchange record, its state and its events are untouched.
