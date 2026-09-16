# Copyright 2020 ACSONE SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import hashlib
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any


@dataclass
class EDIExchangeActionResult:
    """Represents an exchange action result

    Such actions would usually return a simple ``str``; use this class to store the
    result and add a custom message to it.
    """

    output: Any = None
    message: str | None = None

    @classmethod
    def from_result(cls, result: Any) -> "EDIExchangeActionResult":
        """Wraps ``result```` in an ``EDIExchangeActionResult``

        By default, instances created using this method will contain no message.
        """
        return result if isinstance(result, cls) else cls(output=result, message=None)

    @classmethod
    def wrap_result(cls, func: Callable) -> Callable:
        """Wrapper to convert returned values into ``EDIExchangeActionResult`` instances

        By default, instances created using this decorator will contain no message.
        """

        @wraps(func)
        def wrapper(*args, **kwargs) -> "EDIExchangeActionResult":
            return cls.from_result(func(*args, **kwargs))

        return wrapper


def normalize_string(cls, a_string, sep="_"):
    """Normalize given string, replace dashes with given separator."""
    return cls.env["ir.http"]._slugify(a_string).replace("-", sep)


def get_checksum(filecontent):
    return hashlib.md5(filecontent).hexdigest()
