# Copyright 2024 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import datetime

import pytz
from psycopg2.extensions import AsIs

from odoo import _, api, exceptions, fields, models
from odoo.tools import DotDict, safe_eval


def date_to_datetime(dt):
    """Convert date to datetime."""
    if isinstance(dt, datetime.date):
        return datetime.datetime.combine(dt, datetime.datetime.min.time())
    return dt


def to_utc(dt):
    """Convert date or datetime to UTC."""
    # Gracefully convert to datetime if needed 1st
    return date_to_datetime(dt).astimezone(pytz.UTC)


class EdiConfiguration(models.Model):
    _name = "edi.configuration"
    _description = """
        This model is used to configure EDI (Electronic Data Interchange) flows.
        It allows users to create their own configurations, which can be tailored
        to meet the specific needs of their business processes.
    """

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    description = fields.Char(help="Describe what the conf is for")
    backend_id = fields.Many2one(string="Backend", comodel_name="edi.backend")
    # Field `type_id` is not a mandatory field because we will create 2 common confs
    # for EDI (`send_via_email` and `send_via_edi`). So type_id is
    # a mandatory field will create unwanted data for users when installing this module.
    type_id = fields.Many2one(
        string="Exchange Type",
        comodel_name="edi.exchange.type",
        ondelete="cascade",
        auto_join=True,
        index=True,
    )
    model_id = fields.Many2one(
        "ir.model",
        string="Model",
        help="Model the conf applies to. Leave blank to apply for all models",
    )
    model_name = fields.Char(
        related="model_id.model", store=True, string="Model tech name"
    )
    trigger_id = fields.Many2one(
        string="Trigger",
        comodel_name="edi.configuration.trigger",
        help="Trigger that activates this configuration",
        domain="['|', ('model_id', '=', model_id), ('model_id', '=', False)]",
    )
    trigger = fields.Char(related="trigger_id.code")
    snippet_before_do = fields.Text(
        help="Snippet to validate the state and collect records to do",
    )
    snippet_do = fields.Text(
        help="""Used to do something specific here.
        Receives: operation, edi_action, vals, old_vals.""",
    )

    @api.constrains("backend_id", "type_id")
    def _constrains_backend(self):
        for rec in self:
            if rec.type_id.backend_id:
                if rec.type_id.backend_id != rec.backend_id:
                    raise exceptions.ValidationError(
                        _("Backend must match with exchange type's backend!")
                    )
            else:
                if rec.type_id.backend_type_id != rec.backend_id.backend_type_id:
                    raise exceptions.ValidationError(
                        _("Backend type must match with exchange type's backend type!")
                    )

    # TODO: This function is also available in `edi_exchange_template`.
    # Consider adding this to util or mixin
    def _code_snippet_valued(self, snippet):
        snippet = snippet or ""
        return bool(
            [
                not line.startswith("#")
                for line in (snippet.splitlines())
                if line.strip("")
            ]
        )

    @staticmethod
    def _date_to_string(dt, utc=True):
        if not dt:
            return ""
        if utc:
            dt = to_utc(dt)
        return fields.Date.to_string(dt)

    @staticmethod
    def _datetime_to_string(dt, utc=True):
        if not dt:
            return ""
        if utc:
            dt = to_utc(dt)
        return fields.Datetime.to_string(dt)

    def _time_utils(self):
        return {
            "datetime": safe_eval.datetime,
            "dateutil": safe_eval.dateutil,
            "time": safe_eval.time,
            "utc_now": fields.Datetime.now(),
            "date_to_string": self._date_to_string,
            "datetime_to_string": self._datetime_to_string,
            "time_to_string": lambda dt: dt.strftime("%H:%M:%S") if dt else "",
            "first_of": fields.first,
        }

    def _get_code_snippet_eval_context(self):
        """Prepare the context used when evaluating python code

        :returns: dict -- evaluation context given to safe_eval
        """
        ctx = {
            "uid": self.env.uid,
            "user": self.env.user,
            "DotDict": DotDict,
            "conf": self,
        }
        ctx.update(self._time_utils())
        return ctx

    def _evaluate_code_snippet(self, snippet, **render_values):
        if not self._code_snippet_valued(snippet):
            return {}
        eval_ctx = dict(render_values, **self._get_code_snippet_eval_context())
        safe_eval.safe_eval(snippet, eval_ctx, mode="exec", nocopy=True)
        result = eval_ctx.get("result", {})
        if not isinstance(result, dict):
            return {}
        return result

    def edi_exec_snippet_before_do(self, record, **kwargs):
        self.ensure_one()
        # Execute snippet before do
        vals_before_do = self._evaluate_code_snippet(
            self.snippet_before_do, record=record, **kwargs
        )

        # Prepare data
        vals = {
            "todo": vals_before_do.get("todo", True),
            "conf": self,
            "snippet_do_vars": vals_before_do.get("snippet_do_vars", False),
            "event_only": vals_before_do.get("event_only", False),
            "tracked_fields": vals_before_do.get("tracked_fields", False),
            "edi_action": vals_before_do.get("edi_action", False),
        }
        return vals

    def edi_exec_snippet_do(self, record, **kwargs):
        self.ensure_one()
        if self.trigger == "disabled":
            return False

        old_value = kwargs.get("old_vals", {}).get(record.id, {})
        new_value = kwargs.get("vals", {}).get(record.id, {})
        vals = {
            "todo": True,
            "conf": self,
            "record": record,
            "operation": kwargs.get("operation", False),
            "edi_action": kwargs.get("edi_action", False),
            "old_value": old_value,
            "vals": new_value,
        }
        if self.snippet_before_do:
            before_do_vals = self.edi_exec_snippet_before_do(record, **kwargs)
            vals.update(before_do_vals)
        if vals["todo"]:
            return self._evaluate_code_snippet(self.snippet_do, **vals)
        return True

    def edi_get_conf(self, trigger, backend=None):
        domain = [("trigger", "=", trigger)]
        if backend:
            domain.append(("backend_id", "=", backend.id))
        else:
            # We will only get confs that have backend_id = False
            # or are equal to self.type_id.backend_id.id
            backend_ids = self.mapped("type_id.backend_id.id")
            backend_ids.append(False)
            domain.append(("backend_id", "in", backend_ids))
        return self.filtered_domain(domain)

    def action_view_partners(self):
        # TODO: add tests
        partner_model = self.env["res.partner"]
        partner_ids = set()
        # Find partners linked to this conf no matter which field
        for field in partner_model._fields.values():
            if field.type == "many2many" and field.comodel_name == self._name:
                query = "SELECT DISTINCT(partner_id) FROM %(table)s WHERE conf_id=%(conf_id)s"
                self.env.cr.execute(
                    query, {"table": AsIs(field.relation), "conf_id": self.id}
                )
                partner_ids.update([r[0] for r in self.env.cr.fetchall()])
        return {
            "type": "ir.actions.act_window",
            "name": _("Partners"),
            "res_model": "res.partner",
            "view_mode": "tree,form",
            "domain": [("id", "in", list(partner_ids))],
        }
