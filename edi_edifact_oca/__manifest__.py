# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "EDI EDIFACT",
    "summary": """Define EDI backend type for EDIFACT.""",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/edi-framework",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "maintainers": ["simahawk"],
    "depends": ["edi_oca", "edi_party_data_oca", "base_edifact"],
    "auto_install": True,
    "data": [
        "data/edi_backend_type.xml",
    ],
    "demo": [
        "demo/edi_backend_demo.xml",
    ],
}
