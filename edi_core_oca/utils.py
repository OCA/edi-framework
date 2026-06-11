# Copyright 2020 ACSONE SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import hashlib


class EdiExchangeReturn:
    """Structured return value for EDI exchange send operations.

    Handlers can return an instance of this class instead of a plain string
    so that callers can distinguish structured results from legacy str returns
    and display rich information (e.g. HTTP status code + diff) as the job
    result.

    Legacy str returns are still supported: callers fall back to
    ``exchange_record._exchange_status_message("send_ok")`` when the result
    is not an ``EdiExchangeReturn`` instance.
    """

    def __init__(self, message, code=None):
        self.message = message
        self.code = code

    def __str__(self):
        if self.code is not None:
            return f"[{self.code}] {self.message}"
        return self.message

    def __repr__(self):
        return f"EdiExchangeReturn(code={self.code!r}, message={self.message!r})"


def normalize_string(cls, a_string, sep="_"):
    """Normalize given string, replace dashes with given separator."""
    return cls.env["ir.http"]._slugify(a_string).replace("-", sep)


def get_checksum(filecontent):
    return hashlib.md5(filecontent).hexdigest()
