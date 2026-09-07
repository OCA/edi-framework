import logging

_logger = logging.getLogger(__name__)


def post_load_hook():
    _logger.info(
        "`edi_exchange_template_party_data` is deprecated and will be removed. "
        "`edi_party_data_oca` (and this glue module) are superseded by "
        "`edi_party_helper_oca`: use its `edi.party.helper` model (or the "
        "`EDIParty` class directly) instead of the `get_party_data` render "
        "context shortcut."
    )
