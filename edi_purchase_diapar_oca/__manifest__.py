# Copyright (C) 2016-Today: Druidoo (<http://www.druidoo.io/>)
# @author: Druidoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

{
    "name": "EDI Purchase DIAPAR",
    "version": "18.0.1.0.0",
    "category": "Custom",
    "author": "Druidoo, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/edi-framework",
    "license": "AGPL-3",
    "depends": [
        "product",
        "purchase_stock",
        "edi_storage_oca",
        "edi_purchase_oca",
        "edi_exchange_template_oca",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/supplier_price_list_views.xml",
        "views/picking_update_views.xml",
        "views/product_template_views.xml",
        "views/res_partner_views.xml",
        "views/exchange_type_views.xml",
        "views/edi_exchange_template_output.xml",
        "views/res_config_settings_views.xml",
        "views/menus.xml",
        "templates/exchange_template_output_diapar.xml",
    ],
    "demo": [
        "demo/fs_storage_demo.xml",
        "demo/edi_backend_type_demo.xml",
        "demo/edi_exchange_template_output_demo.xml",
        "demo/edi_exchange_type_demo.xml",
        "demo/edi_field_mapping_demo.xml",
        "demo/edi_configuration_demo.xml",
    ],
}
