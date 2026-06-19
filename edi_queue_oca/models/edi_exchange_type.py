# Copyright 2021 Camptocamp SA
# Copyright 2025 Dixmit
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from datetime import datetime

import pytz
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

from odoo.addons.base.models.res_partner import _tz_get as timezone_selection


class EdiExchangeType(models.Model):
    _inherit = "edi.exchange.type"

    job_channel_id = fields.Many2one(
        comodel_name="queue.job.channel",
    )
    job_priority = fields.Integer()
    job_eta_enabled = fields.Boolean(
        string="Enable ETA Scheduling",
        help="Accumulate all queue jobs for this exchange type and release them "
        "at the daily time configured below, instead of dispatching each job "
        "immediately. Use this when a trading partner only processes files at a "
        "fixed daily window, or to concentrate resource-intensive EDI work in "
        "off-peak hours.",
    )
    job_eta_hour = fields.Selection(
        [(str(x).zfill(2), str(x).zfill(2)) for x in range(24)],
        string="Execution time - hour",
        help="Hour of the day at which jobs for this type should be scheduled.",
        default="00",
    )
    job_eta_minute = fields.Selection(
        [(str(x).zfill(2), str(x).zfill(2)) for x in range(60)],
        string="Execution time - minute",
        help="Minute of the hour at which jobs for this type should be scheduled.",
        default="00",
    )
    job_eta_tz = fields.Selection(
        timezone_selection,
        string="Execution time - timezone",
        help="ETA's timezone for jobs of this type",
        default=lambda self: self._get_default_eta_tz(),
    )

    @api.model
    def _get_default_eta_tz(self):
        tz_list = timezone_selection(self)
        return self.env.user.tz or (tz_list and tz_list[0][0]) or "UTC"

    def _get_job_eta(self):
        """Returns the ETA for the current type as timezone-naive datetime"""
        self.ensure_one()
        if (
            not self.job_eta_enabled
            or not self.job_eta_tz
            or not self.job_eta_hour
            or not self.job_eta_minute
        ):
            return None

        self.ensure_one()
        now = pytz.UTC.localize(datetime.utcnow())
        eta = (
            pytz.timezone(self.job_eta_tz)
            .localize(
                datetime(
                    now.year,
                    now.month,
                    now.day,
                    int(self.job_eta_hour),
                    int(self.job_eta_minute),
                )
            )
            .astimezone(pytz.UTC)
        )
        if eta < now:
            eta += relativedelta(days=1)
        return eta.replace(tzinfo=None)
