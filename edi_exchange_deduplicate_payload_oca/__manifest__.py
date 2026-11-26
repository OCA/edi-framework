# Copyright 2026 Camptocamp SA
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "EDI Exchange Deduplicate Payload",
    "summary": "Do not send payloads already exported, mark them as obsolete",
    "version": "19.0.1.0.0",
    "category": "EDI",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/edi-framework",
    "license": "LGPL-3",
    "maintainers": ["simahawk"],
    "depends": [
        "edi_exchange_deduplicate_oca",
        "edi_payload_tracking_oca",
    ],
    "data": [
        "views/edi_exchange_type_views.xml",
    ],
}
