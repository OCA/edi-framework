# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "EDI Account Invoice EDIFACT",
    "summary": """
        Configuration and special behaviors for EDI on Invoice.
    """,
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "license": "AGPL-3",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/edi-framework",
    "depends": [
        "edi_account_oca",
        "edi_edifact_oca",
        "account_invoice_edifact",
    ],
    "demo": [
        "demo/edi_exchange_type.xml",
    ],
}
