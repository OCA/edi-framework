# Copyright 2020 ACSONE
# Copyright 2021 Camptocamp
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "EDI",
    "summary": """
    Define backends, exchange types, exchange records,
    basic automation and views for handling EDI exchanges.
    """,
    "version": "18.0.1.5.1",
    "website": "https://github.com/OCA/edi-framework",
    "development_status": "Beta",
    "license": "LGPL-3",
    "author": "ACSONE,Dixmit,Camptocamp,Odoo Community Association (OCA)",
    "maintainers": ["simahawk", "etobella"],
    "depends": [
        "base_edi",
        "mail",
        "base_sparse_field",
    ],
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
    "external_dependencies": {"python": ["PyYAML", "openupgradelib"]},
    "data": [
        "wizards/edi_exchange_record_create_wiz.xml",
        "data/cron.xml",
        "data/ir_actions_server.xml",
        "data/sequence.xml",
        "data/edi_configuration.xml",
        "security/res_groups.xml",
        "security/ir_model_access.xml",
        "views/edi_backend_views.xml",
        "views/edi_backend_type_views.xml",
        "views/edi_exchange_record_views.xml",
        "views/edi_exchange_type_views.xml",
        "views/edi_exchange_type_rule_views.xml",
        "views/edi_configuration_views.xml",
        "views/edi_configuration_trigger_views.xml",
        "views/res_partner.xml",
        "views/menuitems.xml",
        "templates/exchange_chatter_msg.xml",
        "templates/exchange_mixin_buttons.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "edi_core_oca/static/src/js/widget_edi.esm.js",
            "edi_core_oca/static/src/xml/widget_edi.xml",
        ],
    },
    "demo": ["demo/edi_backend_demo.xml"],
    "installable": True,
}
