# Copyright 2020 ACSONE SA
# Copyright 2020 Creu Blanca
# Copyright 2021 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


import logging

from odoo import _, models

from odoo.addons.component.exception import NoComponentError

_logger = logging.getLogger(__name__)


class EDIBackend(models.Model):
    _name = "edi.backend"
    _inherit = [_name, "collection.base"]

    def _get_component(self, exchange_record, key):
        record_conf = self._get_component_conf_for_record(exchange_record, key)
        # Load additional ctx keys if any
        collection = self
        # TODO: document/test this
        env_ctx = self._get_component_env_ctx(record_conf, key)
        collection = collection.with_context(**env_ctx)
        exchange_record = exchange_record.with_context(**env_ctx)
        work_ctx = {"exchange_record": exchange_record}
        # Inject work context from advanced settings
        work_ctx.update(record_conf.get("work_ctx", {}))
        # Model is not granted to be there
        model = exchange_record.model or self._name
        candidates = self._get_component_usage_candidates(exchange_record, key)
        match_attrs = self._component_match_attrs(exchange_record, key)
        return collection._find_component(
            model,
            candidates,
            work_ctx=work_ctx,
            **match_attrs,
        )

    def _get_component_env_ctx(self, record_conf, key):
        env_ctx = record_conf.get("env_ctx", {})
        # You can use `edi_session` down in the stack to control logics.
        env_ctx.update(dict(edi_framework_action=key))
        return env_ctx

    def _component_match_attrs(self, exchange_record, key):
        """Attributes that will be used to lookup components.

        They will be set in the work context and propagated to components.
        """
        return {
            "backend_type": self.backend_type_id.code,
            "exchange_type": exchange_record.type_id.code,
        }

    def _component_sort_key(self, component_class):
        """Determine the order of matched components.

        The order can be very important if your implementation
        allow generic / default components to be registered.
        """
        return (
            1 if component_class._backend_type else 0,
            1 if component_class._exchange_type else 0,
        )

    def _find_component(self, model, usage_candidates, safe=True, work_ctx=None, **kw):
        """Retrieve component for current backend.

        :param usage_candidates:
            list of usage to try by priority. 1st found, 1st returned
        :param safe: boolean, if true does not break if component is not found
        :param work_ctx: dictionary with work context params
        :param kw: keyword args to lookup for components (eg: usage)
        """
        component = None
        work_ctx = work_ctx or {}
        if "backend" not in work_ctx:
            work_ctx["backend"] = self
        with self.work_on(model, **work_ctx) as work:
            for usage in usage_candidates:
                components, c_work_ctx = work._matching_components(usage=usage, **kw)
                if not components:
                    continue
                # Sort components and pick the 1st one matching.
                # In this way we support generic components registration
                # and specific components registrations
                components = sorted(
                    components, key=lambda x: self._component_sort_key(x), reverse=True
                )
                component = components[0](c_work_ctx)
                _logger.debug("using component %s", component._name)
                break
        if not component and not safe:
            raise NoComponentError(
                f"No component found matching any of: {usage_candidates}"
            )
        return component or None

    def _get_component_usage_candidates(self, exchange_record, key):
        """Retrieve usage candidates for components."""
        # fmt:off
        base_usage = ".".join([
            exchange_record.direction,
            key,
        ])
        # fmt:on
        record_conf = self._get_component_conf_for_record(exchange_record, key)
        candidates = [record_conf["usage"]] if record_conf else []
        candidates += [
            base_usage,
        ]
        return candidates

    def _get_component_conf_for_record(self, exchange_record, key):
        settings = exchange_record.type_id.get_settings()
        return settings.get("components", {}).get(key, {})

    def _exchange_generate(self, exchange_record, **kw):
        component = self._get_component(exchange_record, "generate")
        if component:
            return component.generate()
        return super()._exchange_generate(exchange_record, **kw)

    # TODO: add tests
    def _validate_data(self, exchange_record, value=None, **kw):
        res = super()._validate_data(exchange_record, value=value, **kw)
        if (
            res
            and exchange_record.direction == "input"
            and not exchange_record.exchange_file
        ):
            if not exchange_record.type_id.allow_empty_files_on_receive:
                raise ValueError(
                    _(
                        "Empty files are not allowed for exchange "
                        "type %(name)s (%(code)s)"
                    )
                    % {
                        "name": exchange_record.type_id.name,
                        "code": exchange_record.type_id.code,
                    }
                )

        component = self._get_component(exchange_record, "validate")
        if component:
            return component.validate(value)
        return res

    def _exchange_send(self, exchange_record):
        component = self._get_component(exchange_record, "send")
        if component:
            return component.send()
        return super()._exchange_send(exchange_record)

    def _exchange_output_check_state(self, exchange_record):
        component = self._get_component(exchange_record, "check")
        if component:
            return component.check()
        return super()._exchange_output_check_state(exchange_record)

    def _exchange_process(self, exchange_record):
        component = self._get_component(exchange_record, "process")
        if component:
            return component.process()
        return super()._exchange_process(exchange_record)

    def _exchange_receive(self, exchange_record):
        component = self._get_component(exchange_record, "receive")
        if component:
            return component.receive()
        return super()._exchange_receive(exchange_record)

    def exchange_generate(self, exchange_record, store=True, force=False, **kw):
        res = super().exchange_generate(exchange_record, store=store, force=force, **kw)
        message = None
        state = exchange_record.edi_exchange_state
        if store and state == "output_pending" and exchange_record.exchange_file:
            message = exchange_record._exchange_status_message("generate_ok")
        elif store and state == "validate_error":
            message = exchange_record._exchange_status_message("validate_ko")
        exchange_record.notify_action_complete("generate", message=message)
        return res

    def exchange_send(self, exchange_record):
        """Send exchange file."""
        res = super().exchange_send(exchange_record)
        message = res
        state = exchange_record.edi_exchange_state
        if state == "output_error_on_send":
            message = exchange_record._exchange_status_message("send_ko")
        exchange_record.notify_action_complete("send", message=message)
        return res

    def exchange_process(self, exchange_record):
        old_state = exchange_record.edi_exchange_state
        res = super().exchange_process(exchange_record)
        state = exchange_record.edi_exchange_state
        if state == "input_processed_error" and old_state != "input_processed_error":
            exchange_record._notify_error("process_ko")
        elif state == "input_processed":
            exchange_record._notify_done()
        exchange_record.notify_action_complete("process")
        return res

    def exchange_receive(self, exchange_record):
        res = super().exchange_receive(exchange_record)
        state = exchange_record.edi_exchange_state
        message = res
        if state == "validate_error":
            message = exchange_record._exchange_status_message("validate_ko")
        elif state == "input_receive_error":
            message = exchange_record._exchange_status_message("receive_ko")
        exchange_record.notify_action_complete("receive", message=message)
        return res
