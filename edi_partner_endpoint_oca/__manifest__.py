# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "EDI Partner Endpoint Glue",
    "summary": """
        Glue module between edi_partner_oca and edi_endpoint_oca.""",
    "version": "18.0.1.0.0",
    "development_status": "Alpha",
    "license": "AGPL-3",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/edi-framework",
    "depends": [
        "edi_partner_oca",
        "edi_endpoint_oca",
    ],
    "data": [
        "views/partner_views.xml",
    ],
    "auto_install": True,
}
