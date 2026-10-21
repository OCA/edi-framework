# Copyright 2020 ACSONE SA
# Copyright 2023 Camptocamp
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo.addons.queue_job.job import identity_exact_hasher


def exchange_record_job_identity_exact(job_):
    hasher = identity_exact_hasher(job_)
    # Include files checksum
    hasher.update(
        str(sorted(job_.recordset.mapped("exchange_filechecksum"))).encode("utf-8")
    )
    return hasher.hexdigest()
