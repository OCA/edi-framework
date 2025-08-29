# Copyright 2020 ACSONE SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import hashlib


def normalize_string(cls, a_string, sep="_"):
    """Normalize given string, replace dashes with given separator."""
    return cls.env["ir.http"]._slugify(a_string).replace("-", sep)


def get_checksum(filecontent):
    return hashlib.md5(filecontent).hexdigest()
