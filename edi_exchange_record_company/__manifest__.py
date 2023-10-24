# Copyright 2023 ForgeFlow
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "EDI Exchange Record Company",
    "summary": """
    This module allows you to associate an EDI exchange record with a company.
    """,
    "version": "16.0.1.0.0",
    "website": "https://github.com/OCA/edi-framework",
    "development_status": "Beta",
    "license": "LGPL-3",
    "author": "ForgeFlow,Odoo Community Association (OCA)",
    "depends": [
        "edi_oca",
    ],
    "data": [
        "security/edi_exchange_record_security.xml",
        "views/edi_exchange_record_views.xml",
    ],
    "application": False,
    "installable": True,
}
