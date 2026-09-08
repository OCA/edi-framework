# Copyright 2024 Camptocamp
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Edi Exchange Deduplicate OCA",
    "summary": """
        Mark superseded exchange records as obsolete""",
    "version": "19.0.2.0.0",
    "license": "LGPL-3",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "maintainers": ["simahawk", "etobella"],
    "website": "https://github.com/OCA/edi-framework",
    "depends": ["edi_core_oca"],
    "data": [
        "data/cron.xml",
        "views/edi_exchange_type_views.xml",
    ],
    "demo": [],
}
