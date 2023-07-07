# Copyright 2023 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import datetime
import json
from functools import singledispatch

from odoo import fields

from odoo.addons.base_sparse_field.models.fields import Serialized


@singledispatch
def convert(obj):
    raise TypeError(
        f"Object of type {obj.__class__.__name__} " f"is not JSON serializable"
    )


@convert.register(datetime.date)
def convert_date(obj):
    return fields.Date.to_string(obj)


@convert.register(datetime.datetime)
def convert_datetime(obj):
    return fields.Datetime.to_string(obj)


class ExtendedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        return convert(obj)


# ATM there's no control over the encoder of Serialized field.
# Hence, we must use our own field.
# TODO: propose configurable param on odoo master.
class BetterSerialized(Serialized):
    """Serialize fields w/ proper JSON encoder/decoder"""

    def convert_to_cache(self, value, record, validate=True):
        return (
            json.dumps(value, cls=ExtendedJSONEncoder)
            if isinstance(value, dict)
            else (value or None)
        )
