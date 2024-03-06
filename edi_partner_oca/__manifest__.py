# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "EDI Partners",
    "summary": """
       EDI framework configuration and base logic for partners""",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/edi-framework",
    "depends": [
        "contacts",
        "edi_oca",
    ],
    "data": ["views/partner_views.xml"],
}
