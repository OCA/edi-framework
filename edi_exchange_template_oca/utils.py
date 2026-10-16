# Copyright 2020 ACSONE SA/NV
# Copyright 2022 Camptocamp SA
# Copyright 2026 Dixmit
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


def first_of(records):
    try:
        iterable = iter(records)
    except TypeError:
        # not iterable, we will treat it as a single value
        return records
    return next(iterable, None)
