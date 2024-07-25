# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "EDI UTM",
    "summary": """
        Allows to define an utm source on an exchange type.
    """,
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "license": "AGPL-3",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "maintainers": ["simahawk"],
    "website": "https://github.com/OCA/edi-framework",
    "depends": [
        "utm",
        "edi_oca",
    ],
    "data": [
        "data/utm_source.xml",
        "views/edi_exchange_record_views.xml",
    ],
}
