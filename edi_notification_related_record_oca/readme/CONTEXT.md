Every outgoing message logged two notes on the business record that the
people reading it could not act on: one when the exchange data was
generated, and one when it was sent. To a non-technical user those two
are near-redundant — the exchange was going out either way, and the
distinction between "generated" and "sent" is an implementation detail
of the EDI flow rather than something that changes what they should do.

The result was a chatter where the genuinely useful entries were buried
under EDI bookkeeping. Rather than dropping those notes for everyone —
they are valuable while setting a flow up, and on types where the send
really is the business event — the choice of which events are worth
surfacing on the related record is left to configuration.
