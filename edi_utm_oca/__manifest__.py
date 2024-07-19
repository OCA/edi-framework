# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "EDI UTM",
    "summary": """
    Automatically assigns the EDI source to records created through the EDI mechanism.
    """,
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/edi-framework",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["simahawk"],
    "depends": ["utm", "edi_oca"],
    "data": [
        "data/utm_source.xml",
    ],
    "installable": True,
}
