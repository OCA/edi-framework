# Copyright 2026 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "EDI Exchange Record File Manager",
    "summary": "Adds a wizard to manage the file of an EDI exchange record",
    "version": "18.0.1.0.0",
    "website": "https://github.com/OCA/edi-framework",
    "development_status": "Beta",
    "license": "LGPL-3",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "depends": ["edi_core_oca"],
    "data": [
        "security/ir.model.access.csv",
        "views/edi_exchange_record_views.xml",
        "wizards/edi_exchange_record_file_manager.xml",
    ],
    "installable": True,
}
