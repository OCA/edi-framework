# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "EDI Stock OCA",
    "summary": """
       Define EDI Configuration for Stock""",
    "version": "18.0.1.0.1",
    "license": "AGPL-3",
    "author": "Creu Blanca, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/edi-framework",
    "depends": ["stock", "edi_oca", "component_event"],
    "data": [
        "data/edi_configuration.xml",
        "views/stock_picking.xml",
        "views/res_partner.xml",
    ],
    "demo": [
        "demo/edi_backend.xml",
        "demo/edi_exchange_type.xml",
        "demo/edi_configuration.xml",
    ],
}
