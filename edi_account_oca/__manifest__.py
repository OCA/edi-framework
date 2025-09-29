# Copyright 2020 Dixmit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Edi Account",
    "summary": """
        Define EDI Configuration for Account Moves""",
    "version": "18.0.1.1.1",
    "license": "LGPL-3",
    "author": "Dixmit,Odoo Community Association (OCA)",
    "maintainers": ["etobella"],
    "development_status": "Beta",
    "website": "https://github.com/OCA/edi-framework",
    "depends": ["account", "edi_core_oca"],
    "pre_init_hook": "pre_init_hook",
    "data": [
        "views/account_journal.xml",
        "views/res_partner.xml",
        "views/account_move.xml",
        "views/edi_exchange_record.xml",
    ],
    "demo": [],
}
