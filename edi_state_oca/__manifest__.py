# Copyright 2023 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "EDI state",
    "summary": """
    Allow to assign specific EDI states to related records.
    """,
    "version": "14.0.1.0.2",
    "development_status": "Alpha",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/edi-framework",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["simahawk"],
    "depends": ["edi_oca"],
    "data": [
        "security/ir_model_access.xml",
        "views/edi_exchange_type.xml",
        "views/edi_state_workflow.xml",
        "views/edi_state.xml",
        "views/menuitems.xml",
    ],
}
