# Copyright 2024 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "EDI Notification",
    "summary": """Define notification activities on exchange records.""",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/edi-framework",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "depends": [
        "edi_oca",
    ],
    "data": ["data/mail_activity_data.xml", "views/edi_exchange_type_views.xml"],
    "installable": True,
}
