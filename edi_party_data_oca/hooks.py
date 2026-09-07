import logging

_logger = logging.getLogger(__name__)


def post_load_hook():
    _logger.info(
        "`edi_party_data_oca` is deprecated and will be removed. Its "
        "`edi.party.data.mixin` component is superseded by "
        "`edi_party_helper_oca`: use its `edi.party.helper` model (or the "
        "`EDIParty` class directly) instead, they don't require any "
        "component lookup."
    )
