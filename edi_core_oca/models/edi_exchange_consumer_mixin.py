# Copyright 2020 ACSONE SA
# Copyright 2020 Creu Blanca
# Copyright 2022 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from lxml import etree

from odoo import api, fields, models
from odoo.tools import safe_eval
from odoo.tools.misc import frozendict

from odoo.addons.base_sparse_field.models.fields import Serialized


class EDIExchangeConsumerMixin(models.AbstractModel):
    """Record that might have related EDI Exchange records"""

    _name = "edi.exchange.consumer.mixin"
    _description = "Abstract record where exchange records can be assigned"

    origin_exchange_record_id = fields.Many2one(
        string="EDI origin record",
        comodel_name="edi.exchange.record",
        ondelete="set null",
        help="EDI record that originated this document.",
        copy=False,
    )
    origin_exchange_type_id = fields.Many2one(
        string="EDI origin exchange type",
        comodel_name="edi.exchange.type",
        ondelete="set null",
        related="origin_exchange_record_id.type_id",
        # Store it to ease searching by type
        store=True,
        copy=False,
    )
    exchange_record_ids = fields.One2many(
        "edi.exchange.record",
        inverse_name="res_id",
        domain=lambda r: [("model", "=", r._name)],
    )
    exchange_record_count = fields.Integer(compute="_compute_exchange_record_count")
    edi_config = Serialized(
        compute="_compute_edi_config",
        default={},
    )
    edi_has_form_config = fields.Boolean(compute="_compute_edi_config")
    edi_disable_auto = fields.Boolean(
        string="Disable auto",
        help="When marked, EDI automatic processing will be avoided",
        # Each extending module should override `states` as/if needed.
    )

    def _compute_edi_config(self):
        for record in self:
            config = record._edi_get_exchange_type_config()
            record.edi_config = config
            record.edi_has_form_config = any([x.get("form") for x in config.values()])

    def _edi_get_exchange_type_config(self):
        # TODO: move this machinery to the rule model
        rules = (
            self.env["edi.exchange.type.rule"]
            .sudo()
            .search([("model_id.model", "=", self._name)])
        )
        result = {}
        for rule in rules:
            exchange_type = rule.type_id
            eval_ctx = dict(
                self._get_eval_context(), record=self, exchange_type=exchange_type
            )
            domain = safe_eval.safe_eval(rule.enable_domain or "[]", eval_ctx)
            if not self.filtered_domain(domain):
                continue
            if rule.enable_snippet:
                safe_eval.safe_eval(
                    rule.enable_snippet, eval_ctx, mode="exec", nocopy=True
                )
                if not eval_ctx.get("result", False):
                    continue

            result[rule.id] = self._edi_get_exchange_type_rule_conf(rule)
        return result

    @api.model
    def _edi_get_exchange_type_rule_conf(self, rule):
        conf = {
            "form": {},
            "type": {
                "id": rule.type_id.id,
                "name": rule.type_id.name,
            },
        }
        if rule.kind == "form_btn":
            label = rule.form_btn_label or rule.type_id.name
            conf.update(
                {"form": {"btn": {"label": label, "tooltip": rule.form_btn_tooltip}}}
            )
        return conf

    def _get_eval_context(self):
        """Prepare context to evalue python code snippet.

        :returns: dict -- evaluation context given to safe_eval
        """
        return {
            "datetime": safe_eval.datetime,
            "dateutil": safe_eval.dateutil,
            "time": safe_eval.time,
            "uid": self.env.uid,
            "user": self.env.user,
        }

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        res = super().get_view(view_id, view_type, **options)
        if view_type == "form":
            View = self.env["ir.ui.view"]
            if view_id and res.get("base_model", self._name) != self._name:
                View = View.with_context(base_model_name=res["base_model"])
            doc = etree.XML(res["arch"])
            all_models = res["models"].copy()
            # We need to check if the new view modifies or adds new models
            # Theoretically, it should not be modified, but it is wise to keep it
            # Basically we will add new ones later

            # Select main `sheet` only as they can be nested into fields custom forms.
            # I'm looking at you `account.view_move_line_form` on v16 :S
            for node in doc.xpath("//sheet[not(ancestor::field)]"):
                # TODO: add a default group
                group = False
                if hasattr(self, "_edi_generate_group"):
                    group = self._edi_generate_group
                str_element = self.env["ir.qweb"]._render(
                    "edi_oca.edi_exchange_consumer_mixin_buttons",
                    {"group": group},
                )
                new_node = etree.fromstring(str_element)
                new_arch, new_models = View.postprocess_and_fields(new_node, self._name)
                for model in new_models:
                    all_models[model] = tuple(
                        set(all_models.get(model, {})) | set(new_models[model])
                    )
                node.addprevious(etree.fromstring(new_arch))
            res["arch"] = etree.tostring(doc)
            res["models"] = frozendict(all_models)
        return res

    def _edi_create_exchange_record_vals(self, exchange_type):
        return {
            "model": self._name,
            "res_id": self.id,
        }

    def _edi_create_exchange_record(self, exchange_type, backend=None, vals=None):
        backend = exchange_type.backend_id or backend
        assert backend
        vals = vals or {}
        vals.update(self._edi_create_exchange_record_vals(exchange_type))
        return backend.create_record(exchange_type.code, vals)

    def edi_create_exchange_record(self, exchange_type_id):
        self.ensure_one()
        exchange_type = self.env["edi.exchange.type"].browse(exchange_type_id)
        backend = exchange_type.backend_id
        if (
            not backend
            and self.env["edi.backend"].search_count(
                [("backend_type_id", "=", exchange_type.backend_type_id.id)]
            )
            == 1
        ):
            backend = self.env["edi.backend"].search(
                [("backend_type_id", "=", exchange_type.backend_type_id.id)]
            )
            # FIXME: here you can still have more than one backend per type.
            # We should always get to the wizard w/ pre-populated values.
            # Maybe this behavior can be controlled by exc type adv param.
        if backend:
            exchange_record = self._edi_create_exchange_record(exchange_type, backend)
            self._event("on_edi_generate_manual").notify(self, exchange_record)
            return exchange_record.get_formview_action()
        return self._edi_get_create_record_wiz_action(exchange_type_id)

    def _edi_get_create_record_wiz_action(self, exchange_type_id):
        xmlid = "edi_oca.edi_exchange_record_create_act_window"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        action["context"] = {
            "default_res_id": self.id,
            "default_model": self._name,
            "default_exchange_type_id": exchange_type_id,
        }
        return action

    def _has_exchange_record(self, exchange_type, backend=False, extra_domain=False):
        """Check presence of related exchange record with a specific exchange type"""
        return bool(
            self.env["edi.exchange.record"].search_count(
                self._has_exchange_record_domain(
                    exchange_type, backend=backend, extra_domain=extra_domain
                )
            )
        )

    def _has_exchange_record_domain(
        self, exchange_type, backend=False, extra_domain=False
    ):
        if isinstance(exchange_type, str):
            # Backward compat: allow passing the code when method is called directly
            type_leaf = [("type_id.code", "=", exchange_type)]
        else:
            type_leaf = [("type_id", "=", exchange_type.id)]
        domain = [
            ("model", "=", self._name),
            ("res_id", "=", self.id),
        ] + type_leaf
        if backend is None:
            backend = exchange_type.backend_id
        if backend:
            domain.append(("backend_id", "=", backend.id))
        if extra_domain:
            domain += extra_domain
        return domain

    def _get_exchange_record(self, exchange_type, backend=False, extra_domain=False):
        """Get all related exchange records matching give exchange type."""
        return self.env["edi.exchange.record"].search(
            self._has_exchange_record_domain(
                exchange_type, backend=backend, extra_domain=extra_domain
            )
        )

    @api.depends("exchange_record_ids")
    def _compute_exchange_record_count(self):
        data = self.env["edi.exchange.record"].read_group(
            [("res_id", "in", self.ids), ("model", "=", self._name)],
            ["res_id"],
            ["res_id"],
        )
        mapped_data = {x["res_id"]: x["res_id_count"] for x in data}
        for rec in self:
            rec.exchange_record_count = mapped_data.get(rec.id, 0)

    def action_view_edi_records(self):
        self.ensure_one()
        xmlid = "edi_oca.act_open_edi_exchange_record_view"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        action["domain"] = [("model", "=", self._name), ("res_id", "=", self.id)]
        # Purge default search filters from ctx to avoid hiding records
        ctx = action.get("context", {})
        if isinstance(ctx, str):
            ctx = safe_eval.safe_eval(ctx, dict(self.env.context))
        action["context"] = {
            k: v for k, v in ctx.items() if not k.startswith("search_default_")
        }
        # Drop ID otherwise the context will be loaded from the action's record :S
        action.pop("id")
        return action

    @api.model
    def get_edi_access(self, doc_ids, operation, model_name=False):
        """Retrieve access policy.

        The behavior is similar to `mail.thread` and `mail.message`
        and it relies on the access rules defines on the related record.
        The behavior can be customized on the related model
        by defining `_edi_exchange_record_access`.

        By default `write`, otherwise the custom permission is returned.
        """
        DocModel = self.env[model_name] if model_name else self
        create_allow = getattr(DocModel, "_edi_exchange_record_access", "write")
        if operation in ["write", "unlink"]:
            check_operation = "write"
        elif operation == "create" and create_allow in [
            "create",
            "read",
            "write",
            "unlink",
        ]:
            check_operation = create_allow
        elif operation == "create":
            check_operation = "write"
        else:
            check_operation = operation
        return check_operation

    def _edi_set_origin(self, exc_record):
        self.sudo().update({"origin_exchange_record_id": exc_record.id})

    def _edi_get_origin(self):
        self.ensure_one()
        return self.origin_exchange_record_id

    # TODO: full unit test coverage
    def _edi_send_via_edi(self, exchange_type, backend=None, force=False, **kw):
        """Simply sending out a record via EDI.

        If the exchange type requires an ack, it will be generated
        if not already present.
        """
        exchange_record = None
        # If we are sending an ack, we must check if we can generate it
        if exchange_type.ack_for_type_ids:
            # TODO: shall we raise an error if the ack is not possible?
            if self._edi_can_generate_ack(exchange_type):
                __, exchange_record = self._edi_get_or_create_ack_record(
                    exchange_type, force=force
                )
        else:
            exchange_record = self._edi_create_exchange_record(
                exchange_type, backend=backend
            )
        # If quick exec is on, `exchange_generate_send` already ran
        if exchange_record and not exchange_type.quick_exec:
            exchange_record.action_exchange_generate_send(**kw)

    # TODO: full unit test coverage
    def _edi_can_generate_ack(self, exchange_type, force=False):
        """Have to generate ack for this exchange type?

        :param exchange_type: The exchange type to check.

        It should be generated if:
        - automation is not disabled and not forced
        - origin exchange record is set (means it was originated by another record)
        - origin exchange type is compatible with the configured ack types
        """
        if (self.edi_disable_auto and not force) or not self.origin_exchange_record_id:
            return False
        return self.origin_exchange_type_id in exchange_type.ack_for_type_ids

    # TODO: full unit test coverage
    def _edi_get_or_create_ack_record(self, exchange_type, backend=None, force=False):
        """
        Get or create a child record for the given exchange type.

        If the record has not been sent out yet for whatever reason
        (job delayed, job failed, send failed, etc)
        we still want to generate a new up to date record to be sent.

        :param exchange_type: The exchange type to create the record for.
        :param force: If True, force creation of the record in case of ack type.
        """
        if not self._edi_can_generate_ack(exchange_type, force=force):
            return False, False
        parent = self._edi_get_origin()
        # Filter acks that are not valued yet.
        exchange_record = self._get_exchange_record(exchange_type).filtered(
            lambda x: not x.exchange_file
        )
        created = False
        # If the record has not been sent out yet for whatever reason
        # (job delayed, job failed, send failed, etc)
        # we still want to generate a new up to date record to be sent.
        still_pending = exchange_record.edi_exchange_state in (
            "output_pending",
            "output_error_on_send",
        )
        if not exchange_record or still_pending:
            vals = exchange_record._exchange_child_record_values()
            vals["parent_id"] = parent.id
            # NOTE: to fully automatize this,
            # is recommended to enable `quick_exec` on the type
            # otherwise records will have to wait for the cron to pass by.
            exchange_record = self._edi_create_exchange_record(
                exchange_type, backend=backend, vals=vals
            )
            created = True
        return created, exchange_record

    # TODO: full unit test coverage
    def _edi_send_via_email(
        self, ir_action, subtype_ref=None, partner_method=None, partners=None
    ):
        """Send EDI file via email using the provided action."""
        # FIXME: missing generation of the record and adding it as an attachment
        # In this case, the record should be generated immediately
        # and attached to the email.
        # An alternative is to generate the record
        # and have a component to send via email.

        # Retrieve context and composer model
        ctx = ir_action.get("context", {})
        composer_model = self.env[ir_action["res_model"]].with_context(**ctx)

        # Determine subtype and partner_ids dynamically based on model-specific logic
        subtype = subtype_ref and self.env.ref(subtype_ref) or None
        if not subtype:
            return False

        # THIS IS the part that should be delegated to a specific send component
        # It could be also moved to its own module.
        composer = composer_model.create({"subtype_id": subtype.id})
        composer.onchange_template_id_wrapper()

        # Retrieve partners based on provided method or fallback to parameter
        if partner_method and hasattr(self, partner_method):
            composer.partner_ids = getattr(self, partner_method)().ids
        elif partners:
            composer.partner_ids = partners.ids
        else:
            return False

        # Send the email
        composer.send_mail()
        return True

    def write(self, vals):
        # Generic event to match a state change
        # TODO: this can be added to component_event for models having the state field
        state_change = "state" in vals and "state" in self._fields
        if state_change:
            for rec in self:
                rec._event(f"on_edi_{self._table}_before_state_change").notify(
                    rec, state=vals["state"]
                )
        res = super().write(vals)
        if state_change:
            for rec in self:
                rec._event(f"on_edi_{self._table}_state_change").notify(
                    rec, state=vals["state"]
                )
        return res
