# Copyright 2021 Camptocamp SA
# Copyright 2025 Dixmit
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import functools
import logging
from ast import literal_eval

from odoo import api, fields, models

from ..utils import exchange_record_job_identity_exact, render_job_description

_logger = logging.getLogger(__name__)


class EdiExchangeRecord(models.Model):
    _inherit = "edi.exchange.record"

    related_queue_jobs_count = fields.Integer(
        compute="_compute_related_queue_jobs_count"
    )

    def _register_hook(self):
        for function in [
            "action_exchange_send",
            "action_exchange_receive",
            "action_exchange_process",
            "action_exchange_generate",
        ]:
            patched = self._patch_job_auto_delay(function)
            setattr(
                type(self),
                function,
                functools.update_wrapper(
                    patched,
                    getattr(type(self), function),
                ),
            )
        return super()._register_hook()

    def action_exchange_send_job_options(self):
        return {"priority": 0}

    def _job_delay_params(self):
        params = {}
        exchange_type = self.type_id.sudo()
        channel = exchange_type.job_channel_id
        if channel:
            params["channel"] = channel.complete_name
        priority = exchange_type.job_priority
        if priority:
            params["priority"] = priority
        if exchange_type.job_eta_enabled and (eta := exchange_type._get_job_eta()):
            params["eta"] = eta
        # Applied here rather than in the ``<action>_job_options`` methods
        # so that it also covers the chained jobs created by the backend crons
        # and keeps working when an override of the job options does not call
        # super. A ``description`` returned by the job options still wins.
        description = self._job_description_get()
        if description:
            params["description"] = description
        # Avoid generating the same job for the same record if existing
        params["identity_key"] = exchange_record_job_identity_exact
        return params

    @api.model
    def _job_description_placeholders(self):
        """Return the placeholders allowed in job description patterns."""
        return (
            "identifier",
            "external_identifier",
            "type",
            "type_code",
            "backend",
            "record",
        )

    def _job_description_values(self):
        """Return the values of the job description placeholders.

        Missing values are rendered as empty strings.
        """
        self.ensure_one()
        values = dict.fromkeys(self._job_description_placeholders(), "")
        exchange_type = self.type_id.sudo()
        related = self.sudo().record
        values.update(
            {
                "identifier": self.identifier or "",
                "external_identifier": self.external_identifier or "",
                "type": exchange_type.name or "",
                "type_code": exchange_type.code or "",
                "backend": self.backend_id.sudo().name or "",
                "record": related.display_name if related else "",
            }
        )
        return values

    def _job_description_get(self):
        """Return the job description built from the exchange type pattern.

        Return None when there is no pattern, when called on several records
        or when the pattern cannot be rendered (a warning is logged).
        """
        if len(self) != 1:
            return None
        pattern = self.type_id.sudo().job_description_pattern
        if not pattern:
            return None
        try:
            return render_job_description(pattern, self._job_description_values())
        except (ValueError, TypeError) as err:
            _logger.warning(
                "Cannot render job description pattern %r of exchange type %s: %s",
                pattern,
                self.type_id.code,
                err,
            )
            return None

    def with_delay(self, **kw):
        params = self._job_delay_params()
        params.update(kw)
        return super().with_delay(**params)

    def delayable(self, **kw):
        params = self._job_delay_params()
        params.update(kw)
        return super().delayable(**params)

    def _job_retry_params(self):
        return {}

    def _compute_related_queue_jobs_count(self):
        for rec in self:
            # TODO: We should refactor the object field on queue_job to use jsonb field
            # so that we can search directly into it.
            rec.related_queue_jobs_count = rec.env["queue.job"].search_count(
                [("func_string", "like", str(rec))]
            )

    def action_view_related_queue_jobs(self):
        self.ensure_one()
        xmlid = "queue_job.action_queue_job"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        # Searching based on task name:
        # Ex: `edi.exchange.record(1,).action_exchange_send()`
        # TODO: We should refactor the object field on queue_job to use jsonb field
        # so that we can search directly into it.
        action["domain"] = [("func_string", "like", str(self))]
        # Purge default search filters from ctx to avoid hiding records
        ctx = action.get("context", {})
        if isinstance(ctx, str):
            ctx = literal_eval(ctx)
        # Update the current contexts
        ctx.update(self.env.context)
        action["context"] = {
            k: v for k, v in ctx.items() if not k.startswith("search_default_")
        }
        # Drop ID otherwise the context will be loaded from the action's record
        action.pop("id")
        return action

    def action_exchange_generate_send_chained(self):
        job1 = self.delayable().action_exchange_generate()
        # Chain send job.
        # Raise prio to max to send the record out as fast as possible.
        job1.on_done(self.delayable(priority=0).action_exchange_send())
        job1.delay()

    def action_exchange_receive_process_chained(self):
        job1 = self.delayable().action_exchange_receive()
        # Chain process job.
        # Raise prio to max to process the record as soon as it lands.
        job1.on_done(self.delayable(priority=0).action_exchange_process())
        job1.delay()

    def _job_on_fail_generate(self, **kw):
        return self._job_on_fail_update("validate_error", **kw)

    def _job_on_fail_send(self, **kw):
        return self._job_on_fail_update("output_error_on_send", **kw)

    def _job_on_fail_receive(self, **kw):
        return self._job_on_fail_update("input_receive_error", **kw)

    def _job_on_fail_process(self, **kw):
        return self._job_on_fail_update("input_processed_error", **kw)

    def _job_on_fail_update(self, failed_state, **kw):
        self.ensure_one()
        # ``exc_message`` is the first argument of the exception: it is not
        # always a string (e.g. the errno of an ``OSError``) and may be missing.
        error = ": ".join(
            str(kw[k]) for k in ("exc_name", "exc_message") if kw.get(k) is not None
        )
        self.write(
            {
                "edi_exchange_state": failed_state,
                "exchange_error": error,
                "exchange_error_traceback": kw.get("exc_info"),
            }
        )
