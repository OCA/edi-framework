# Copyright 2020 ACSONE SA
# Copyright 2023 Camptocamp
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from string import Formatter

from odoo.addons.queue_job.job import identity_exact_hasher


def exchange_record_job_identity_exact(job_):
    hasher = identity_exact_hasher(job_)
    # Include files checksum
    hasher.update(
        str(sorted(job_.recordset.mapped("exchange_filechecksum"))).encode("utf-8")
    )
    return hasher.hexdigest()


def check_job_description_pattern(pattern, placeholders):
    """Validate a job description pattern.

    Only the named fields listed in ``placeholders`` are accepted:
    positional fields, attribute or index access and unknown names
    raise a ``ValueError``, as well as malformed patterns.
    """
    for __, field_name, format_spec, __ in Formatter().parse(pattern):
        if field_name is None:
            continue
        if field_name not in placeholders:
            raise ValueError(f"unsupported placeholder {{{field_name}}}")
        if format_spec:
            # Nested fields are allowed in the format spec: check them too
            check_job_description_pattern(format_spec, placeholders)


def render_job_description(pattern, values):
    """Render a job description pattern with the given values.

    The pattern is checked first against the keys of ``values``,
    see ``check_job_description_pattern``.
    """
    check_job_description_pattern(pattern, values)
    return pattern.format(**values)
