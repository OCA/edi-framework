# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def post_load_hook():
    """Point installs of this now-empty umbrella to the module they need.

    `edi_webservice_oca` used to hold both the `webservice_backend_id`
    field and the `component`-based send integration; it now only depends
    on both split-out modules to preserve existing installations.
    """
    _logger.info(
        "DEPRECATED - 'edi_webservice_oca' is now just an umbrella kept for backward "
        "compatibility: it depends on both 'edi_webservice_core_oca' "
        "(the 'webservice.backend' link on 'edi.backend', no 'component' "
        "dependency) and 'edi_webservice_component_oca' (the deprecated "
        "'component'-based send integration). New code should depend on "
        "'edi_webservice_core_oca' directly, and additionally on "
        "'edi_webservice_component_oca' only if it actually uses the "
        "'component'-based 'edi.webservice.send' integration."
    )
