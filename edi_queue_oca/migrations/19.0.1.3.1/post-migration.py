# Copyright 2026 Camptocamp SA (http://www.camptocamp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

# The job functions are declared in a ``noupdate`` data file, so databases
# created before the on fail hooks were added never got ``on_fail_method``.
ON_FAIL_METHODS = {
    "edi_queue_oca.job_fun_exchange_record_generate": "_job_on_fail_generate",
    "edi_queue_oca.job_fun_exchange_record_send": "_job_on_fail_send",
    "edi_queue_oca.job_fun_exchange_record_receive": "_job_on_fail_receive",
    "edi_queue_oca.job_fun_exchange_record_process": "_job_on_fail_process",
}


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for xmlid, method in ON_FAIL_METHODS.items():
        job_function = env.ref(xmlid, raise_if_not_found=False)
        if not job_function:
            _logger.warning("Job function %s not found, skipping", xmlid)
            continue
        if job_function.on_fail_method:
            continue
        _logger.info("Setting on_fail_method=%s on %s", method, xmlid)
        job_function.on_fail_method = method
