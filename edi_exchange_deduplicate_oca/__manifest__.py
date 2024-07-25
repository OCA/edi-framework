# Copyright 2024 Camptocamp
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Edi Exchange Deduplicate OCA",
    "summary": """
        Introduce a deduplication mechanism at the sending step""",
    "version": "16.0.1.0.0",
    "license": "LGPL-3",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "maintainers": ["simahawk", "etobella"],
    "website": "https://github.com/OCA/edi-framework",
    "depends": ["edi_oca"],
    "data": [
        "data/cron.xml",
        "views/edi_exchange_type_views.xml",
    ],
    "demo": [],
}
