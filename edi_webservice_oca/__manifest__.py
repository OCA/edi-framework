# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "EDI WebService",
    "summary": """
        Defines webservice integration from EDI Exchange records""",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "development_status": "Beta",
    "author": "Creu Blanca, Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["etobella", "simahawk"],
    "website": "https://github.com/OCA/edi-framework",
    "depends": ["edi_oca", "webservice"],
    "data": ["views/edi_backend.xml", "security/ir.model.access.csv"],
    "demo": ["demo/edi_backend.xml"],
}
