# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "GS1 EDI for stock",
    "summary": """
        Base module for GS1 standard EDI exchange related to stock.
    """,
    "version": "19.0.1.0.0",
    "development_status": "Beta",
    "license": "AGPL-3",
    "author": "ACSONE,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/edi-framework",
    "depends": [
        "edi_gs1_oca",
        "stock",
        "purchase_stock",
        # provides `carrier_id` and `weight` on stock.picking (Odoo 19 moved
        # them out of `delivery` into `stock_delivery`)
        "stock_delivery",
    ],
    "external_dependencies": {"python": ["xmlunittest"]},
    "data": [
        "views/res_config_settings.xml",
        "views/stock_picking_view.xml",
        "data/edi_exchange_type.xml",
        "data/inbound_instruction_qweb_template.xml",
        "data/outbound_instruction_qweb_template.xml",
    ],
}
