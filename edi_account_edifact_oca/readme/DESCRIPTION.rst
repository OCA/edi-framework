Outbound

Send account invoice from EDI channels to the storage system.

On your exchange type, go to advanced settings and add the following::

    [...]
    components:
        generate:
            usage: output.generate.account.move
        send:
            usage: storage.send
