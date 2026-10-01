# Copyright 2026 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "EDI Related Record Notification",
    "summary": """
    Configure, per exchange type and per action, whether a note is posted
    on the chatter of the exchange's related records.
    """,
    "version": "17.0.1.0.0",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/edi-framework",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["GuillemCForgeFlow"],
    "depends": ["edi_oca"],
    "data": ["views/edi_exchange_type_views.xml"],
}
