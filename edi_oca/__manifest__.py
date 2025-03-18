# Copyright 2020 ACSONE
# Copyright 2021 Camptocamp
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "EDI",
    "summary": """
    Define backends, exchange types, exchange records,
    basic automation and views for handling EDI exchanges.
    """,
    "version": "18.0.1.0.0",
    "website": "https://github.com/OCA/edi-framework",
    "development_status": "Beta",
    "license": "LGPL-3",
    "author": "ACSONE,Creu Blanca,Camptocamp,Odoo Community Association (OCA)",
    "maintainers": ["simahawk", "etobella"],
    "depends": [
        "edi_core_oca",
        "component_event",
        "mail",
        "base_sparse_field",
        "queue_job",
    ],
    "data": [],
    "installable": True,
}
