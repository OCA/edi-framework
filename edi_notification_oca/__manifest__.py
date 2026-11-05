# Copyright 2024 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "EDI Notification",
    "summary": """Configure the notifications of exchange records by rules.""",
    "version": "18.0.2.0.0",
    "development_status": "Alpha",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/edi-framework",
    "author": "Camptocamp,ForgeFlow,Odoo Community Association (OCA)",
    # TODO v19: consider getting rid off `edi_component_oca` dep
    "depends": ["edi_core_oca", "edi_component_oca"],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_activity_type.xml",
        "data/edi_notification_trigger.xml",
        "views/edi_exchange_type.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
