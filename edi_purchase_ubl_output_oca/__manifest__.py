# Copyright 2021 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "EDI UBL Purchase",
    "summary": """Handle outbound exchanges for purchases.""",
    "version": "18.0.1.0.1",
    "development_status": "Alpha",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/edi-framework",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["simahawk"],
    "depends": ["edi_purchase_oca", "edi_ubl_oca", "purchase_order_ubl"],
    "demo": [
        "demo/edi_exchange_type.xml",
    ],
}
