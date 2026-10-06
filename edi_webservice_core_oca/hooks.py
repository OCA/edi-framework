# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

import yaml
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

# xids to pass to the new module
MOVED_XMLIDS = [
    "access_webservice_backend_edi_manager",
    "edi_backend_view_form",
]


def pre_init_hook(env):
    """Reuse `edi_webservice_oca`'s pre-split records instead of duplicating them."""
    openupgrade.rename_xmlids(
        env.cr,
        [
            (f"edi_webservice_oca.{xmlid}", f"edi_webservice_core_oca.{xmlid}")
            for xmlid in MOVED_XMLIDS
        ],
    )


def migrate_component_based_exchange_types(env, types=None, handler_model=None):
    """Convert exchange types off the `component`-based webservice send.

    Switches them onto the new, component-free `edi.webservice.send`
    handler. This is an explicit, opt-in tool - NOT run automatically on
    install or upgrade. Staying on `edi_webservice_component_oca` is a
    fully supported choice; this is only for exchange types you actively
    want to move onto the handler/endpoint-based style. Call it by hand,
    e.g. from an Odoo shell, against the types you want migrated::

        from odoo.addons.edi_webservice_core_oca.hooks import (
            migrate_component_based_exchange_types,
        )
        migrated = migrate_component_based_exchange_types(env)

    Pass an explicit `types` recordset to restrict the run (e.g. to test on
    a handful of records first); left out, every `edi.exchange.type` whose
    `send_model_id` is still the generic `component` handler
    (`edi_component_oca.model_edi_oca_component_handler`) and whose backend
    has a `webservice_backend_id` is migrated.

    See `migrate_exchange_type` for what happens to each type.

    """
    component_model = env.ref(
        "edi_component_oca.model_edi_oca_component_handler", raise_if_not_found=False
    )
    if not component_model:
        # `edi_component_oca` was never installed: nothing relied on it.
        return env["edi.exchange.type"].browse()
    if types is None:
        types = env["edi.exchange.type"].search(
            [
                ("send_model_id", "=", component_model.id),
                ("backend_id.webservice_backend_id", "!=", False),
            ]
        )
    handler_model = handler_model or env.ref(
        "edi_webservice_core_oca.model_edi_webservice_send"
    )
    for etype in types:
        migrate_exchange_type(env, etype)
    types.write({"send_model_id": handler_model.id})
    return types


# HELPERS FOR CUSTOM TYPES MIGRATION
#
# Help you convert old style exchange types to no component setup
# and webservice.endpoint usage.
#
# DISCLAIMER: do your own tests!


def migrate_exchange_type(env, etype):
    """Migrate a single exchange type's `component`-based `webservice` settings.

    Updates in place, without touching `send_model_id` (see
    `migrate_component_based_exchange_types`, which also does that).

    Reads the old `components.send.work_ctx.webservice` YAML and applies:

    - `method` is removed - it now lives on the `webservice.endpoint`
      itself, found or created (named after the type's own `code`, unless
      a `webservice_endpoint_id` is already set) and assigned to
      `webservice_endpoint_id`.
    - `send_as_bytes` is removed and moved to the
      `webservice_send_as_bytes` field on the type.
    - `pargs`/`kwargs` are kept (still usable as call-time overrides), just
      moved from `components.send.work_ctx.webservice` to the new
      `execution_model.send.webservice` key.
    - `kwargs.url_params` entries are checked against the backend's own URL:
      a key that fills an actual `{placeholder}` in it stays in
      `url_params` as-is; anything else is a de-facto querystring param, so
      it's moved to a `webservice.querystring.param` on the endpoint
      instead and dropped from the YAML.

    NOTE: rewriting the YAML re-serializes it, so any comments in
    `advanced_settings_edit` are lost for migrated types.

    """
    settings = yaml.safe_load(etype.advanced_settings_edit or "") or {}
    components = settings.get("components", {})
    send_conf = components.get("send", {})
    work_ctx = send_conf.get("work_ctx", {})
    ws_settings = work_ctx.pop("webservice", None)
    if ws_settings is None:
        # Nothing to move: the type relied on the backend-level auto
        # selection without any explicit `webservice` YAML settings.
        return
    if not work_ctx:
        send_conf.pop("work_ctx", None)
    if not send_conf:
        components.pop("send", None)
    if not components:
        settings.pop("components", None)

    method = ws_settings.pop("method", None)
    send_as_bytes = ws_settings.pop("send_as_bytes", None)
    if send_as_bytes is not None:
        etype.webservice_send_as_bytes = bool(send_as_bytes)

    endpoint = etype.webservice_endpoint_id
    if not endpoint:
        if not method:
            _logger.warning(
                "edi.exchange.type(%s): no `method` found in `webservice` "
                "settings, cannot create a webservice.endpoint - please "
                "set `webservice_endpoint_id` manually.",
                etype.id,
            )
        else:
            endpoint = _get_or_create_endpoint(env, etype, method)
            etype.webservice_endpoint_id = endpoint.id

    if endpoint:
        _move_matching_url_params(endpoint, ws_settings)
    if ws_settings:
        settings.setdefault("execution_model", {}).setdefault("send", {})[
            "webservice"
        ] = ws_settings

    etype.advanced_settings_edit = yaml.safe_dump(settings, sort_keys=False)


def _get_or_create_endpoint(env, etype, method):
    ws_backend = etype.backend_id.webservice_backend_id
    tech_name = etype.code
    endpoint = env["webservice.endpoint"].search(
        [("backend_id", "=", ws_backend.id), ("tech_name", "=", tech_name)], limit=1
    )
    if endpoint:
        return endpoint
    endpoint = env["webservice.endpoint"].create(
        {
            "name": etype.name,
            "tech_name": tech_name,
            "description": (
                f"Auto-migrated from exchange type '{etype.code}' " "advanced settings."
            ),
            "backend_id": ws_backend.id,
            "http_method": method.lower(),
        }
    )
    _logger.info(
        "edi.exchange.type(%s): created webservice.endpoint(%s) from "
        "advanced settings.",
        etype.id,
        endpoint.id,
    )
    return endpoint


def _move_matching_url_params(endpoint, ws_settings):
    """Split `ws_settings["kwargs"]["url_params"]` between path and querystring.

    A key that fills a real `{placeholder}` in the backend's URL is kept
    as-is; anything else is moved to the endpoint's own static
    querystring config.

    """
    kwargs = ws_settings.get("kwargs", {})
    url_params = kwargs.get("url_params")
    if not url_params:
        return
    backend_url = endpoint.backend_id.url or ""
    remaining = {}
    for key, value in url_params.items():
        if f"{{{key}}}" in backend_url:
            remaining[key] = value
            continue
        existing = endpoint.env["webservice.querystring.param"].search(
            [
                ("res_model", "=", "webservice.endpoint"),
                ("res_id", "=", endpoint.id),
                ("name", "=", key),
            ],
            limit=1,
        )
        if not existing:
            endpoint.env["webservice.querystring.param"].create(
                {
                    "res_model": "webservice.endpoint",
                    "res_id": endpoint.id,
                    "name": key,
                    "value": value,
                }
            )
    if remaining:
        kwargs["url_params"] = remaining
    else:
        kwargs.pop("url_params", None)
    if not kwargs:
        ws_settings.pop("kwargs", None)
