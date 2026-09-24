# Copyright 2020 Dixmit
# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "EDI WebService Core",
    "summary": """
        Webservice backend and send handler for EDI: no component
        dependency""",
    "version": "18.0.1.1.0",
    "license": "AGPL-3",
    "development_status": "Beta",
    "author": "Dixmit, Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["etobella", "simahawk"],
    "website": "https://github.com/OCA/edi-framework",
    "depends": ["edi_core_oca", "webservice_core"],
    "data": ["views/edi_backend.xml", "security/ir.model.access.csv"],
    "demo": ["demo/edi_backend.xml"],
    "pre_init_hook": "pre_init_hook",
}
