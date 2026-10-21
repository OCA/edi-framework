# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "EDI UBL Output Base",
    "summary": """
        Generic UBL party/address qweb templates for the EDI framework.
    """,
    "version": "18.0.1.3.0",
    "development_status": "Beta",
    "license": "AGPL-3",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/edi-framework",
    "depends": [
        "edi_exchange_template_oca",
    ],
    "data": [
        "templates/qweb_tmpl_party.xml",
    ],
}
