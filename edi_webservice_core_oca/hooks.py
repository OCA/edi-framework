# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import re
from urllib.parse import parse_qsl, urlsplit, urlunsplit

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

    See `migrate_exchange_type` for what happens to each type. Placeholders
    moved to an endpoint path are removed from the backend URL here, once
    all types are processed.

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
    moved_keys_by_backend = {}
    for etype in types:
        backend = etype.backend_id.webservice_backend_id
        moved_keys = migrate_exchange_type(env, etype)
        moved_keys_by_backend.setdefault(backend, set()).update(moved_keys or ())
    # Strip only once every type was classified, so that a placeholder
    # removed for one type is still recognised for the others on that backend.
    for backend, keys in moved_keys_by_backend.items():
        if not backend:
            continue
        backend.url = _strip_url_placeholders(backend.url, keys)
        _move_url_query_to_params(backend)
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
      a key that fills a `{placeholder}` in it becomes the endpoint's
      `path` and is dropped from the YAML; anything else stays in
      `url_params` for manual review.

    NOTE: rewriting the YAML re-serializes it, so any comments in
    `advanced_settings_edit` are lost for migrated types.

    Returns the set of `url_params` keys moved to an endpoint path.

    """
    settings = yaml.safe_load(etype.advanced_settings_edit or "") or {}
    components = settings.get("components", {})
    send_conf = components.get("send", {})
    work_ctx = send_conf.get("work_ctx", {})
    ws_settings = work_ctx.pop("webservice", None)
    if ws_settings is None:
        # Nothing to move: the type relied on the backend-level auto
        # selection without any explicit `webservice` YAML settings.
        return set()
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

    moved_keys = set()
    if endpoint:
        moved_keys = _move_matching_url_params(endpoint, ws_settings)
    if ws_settings:
        settings.setdefault("execution_model", {}).setdefault("send", {})[
            "webservice"
        ] = ws_settings

    etype.advanced_settings_edit = yaml.safe_dump(settings, sort_keys=False)
    return moved_keys


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
    """Move `{placeholder}` url_params into the endpoint's path.

    A key that fills a `{placeholder}` in the backend's URL becomes the
    endpoint's `path`, and is dropped from the YAML. Anything else is kept
    in the YAML `url_params` for manual review (no querystring param is
    created from it).

    Returns the set of keys moved to the path.

    """
    kwargs = ws_settings.get("kwargs", {})
    url_params = kwargs.get("url_params")
    if not url_params:
        return set()
    backend_url = endpoint.backend_id.url or ""
    remaining = {}
    moved = set()
    for key, value in url_params.items():
        if f"{{{key}}}" not in backend_url:
            _logger.warning(
                "webservice.endpoint(%s): url_param %r is not a placeholder in "
                "the backend URL, kept in YAML for manual review.",
                endpoint.id,
                key,
            )
            remaining[key] = value
            continue
        if endpoint.path and endpoint.path != value:
            _logger.warning(
                "webservice.endpoint(%s): path already set to %r, url_param "
                "%r=%r kept in YAML for manual review.",
                endpoint.id,
                endpoint.path,
                key,
                value,
            )
            remaining[key] = value
            continue
        endpoint.path = value
        stale = endpoint.querystring_param_ids.filtered(lambda p, k=key: p.name == k)
        if stale:
            _logger.info(
                "webservice.endpoint(%s): removing querystring param %r, "
                "now carried by the endpoint path.",
                endpoint.id,
                key,
            )
            stale.unlink()
        moved.add(key)
    if remaining:
        kwargs["url_params"] = remaining
    else:
        kwargs.pop("url_params", None)
    if not kwargs:
        ws_settings.pop("kwargs", None)
    return moved


def _strip_url_placeholders(url, keys):
    for key in keys:
        url = re.sub(r"/?\{" + re.escape(key) + r"\}", "", url or "")
    return url


def _move_url_query_to_params(backend):
    parts = urlsplit(backend.url or "")
    if not parts.query:
        return
    existing = backend.querystring_param_ids.mapped("name")
    pairs = [
        (name, value)
        for name, value in parse_qsl(parts.query, keep_blank_values=True)
        if name not in existing
    ]
    backend.env["webservice.querystring.param"].create(
        [
            {
                "res_model": backend._name,
                "res_id": backend.id,
                "name": name,
                "value": value,
            }
            for name, value in pairs
        ]
    )
    backend.url = urlunsplit(
        (parts.scheme, parts.netloc, parts.path, "", parts.fragment)
    )
