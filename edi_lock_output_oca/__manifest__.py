# Copyright 2026 Camptocamp SA
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "EDI Lock Output",
    "summary": "Lock fields of records once their EDI output was sent",
    "version": "19.0.1.0.0",
    "category": "EDI",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/edi-framework",
    "license": "LGPL-3",
    "maintainers": ["simahawk"],
    "depends": [
        "edi_core_oca",
    ],
    "data": [
        "security/res_groups.xml",
        "views/edi_exchange_type_views.xml",
    ],
}
