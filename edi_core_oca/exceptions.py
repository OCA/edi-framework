# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


class EDIValidationError(Exception):
    """Thrown when a document validation fails."""


class EDINotImplementedError(NotImplementedError):
    """Thrown when a method is not implemented for a specific backend."""
