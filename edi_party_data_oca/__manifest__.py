# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "EDI Party data",
    "summary": """
    Allow to configure and retrieve party information for EDI exchanges.
    """,
    "version": "18.0.1.1.1",
    "development_status": "Alpha",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/edi-framework",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["simahawk"],
    "depends": ["edi_component_oca", "edi_party_helper_oca"],
    "post_load_hook": "post_load_hook",
}
