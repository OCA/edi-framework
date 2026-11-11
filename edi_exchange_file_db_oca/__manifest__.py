# Copyright 2026 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "EDI Exchange File in Database",
    "summary": """
    Store the files of EDI exchange records in the database instead of the
    filestore.
    """,
    "version": "17.0.1.0.0",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/edi-framework",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["GuillemCForgeFlow"],
    "depends": ["edi_oca"],
    "data": [
        "data/ir_config_parameter.xml",
        "views/edi_exchange_record_views.xml",
        "views/edi_exchange_type_views.xml",
    ],
    "post_init_hook": "post_init_hook",
}
