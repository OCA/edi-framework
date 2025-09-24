# Copyright 2025 Dixmit
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging

from odoo import models

from odoo.addons.component.exception import NoComponentError

_logger = logging.getLogger(__name__)


class EdiBackend(models.Model):
    _name = "edi.backend"
    _inherit = ["edi.backend", "collection.base"]

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

    def _get_component_env_ctx(self, record_conf, key):
        env_ctx = record_conf.get("env_ctx", {})
        # You can use `edi_session` down in the stack to control logics.
        env_ctx.update(dict(edi_framework_action=key))
        return env_ctx
