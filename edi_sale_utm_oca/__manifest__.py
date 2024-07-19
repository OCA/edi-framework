# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "EDI Sale UTM",
    "summary": """
    Automatically set edi source on the sale order when it is created.
    """,
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/edi-framework",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["simahawk"],
    "depends": ["edi_sale_oca", "edi_utm_oca"],
    "data": [
        "views/sale_order.xml",
    ],
    "installable": True,
}
