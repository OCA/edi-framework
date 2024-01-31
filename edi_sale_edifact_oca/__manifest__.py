# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "EDI Sales EDIFACT",
    "summary": """
        Provide a demo exchange type setting and common tests for EDIFACT standard
        in EDI on sales.
    """,
    "version": "16.0.1.1.0",
    "development_status": "Alpha",
    "license": "AGPL-3",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/edi-framework",
    "depends": [
        "sale_order_import_edifact",
        "edi_sale_oca",
        "edi_edifact_oca",
        "sale_stock",
    ],
    "demo": [
        "demo/edi_exchange_type.xml",
    ],
}
