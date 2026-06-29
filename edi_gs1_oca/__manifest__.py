# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Base GS1 EDI",
    "summary": """
        Base module for GS1 standard EDI exchange""",
    "version": "19.0.1.0.0",
    "development_status": "Alpha",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/edi-framework",
    "author": "ACSONE,Odoo Community Association (OCA)",
    "depends": ["edi_core_oca", "uom"],
    "external_dependencies": {"python": ["xmlschema", "xmlunittest"]},
    "data": [
        "data/gs1_backend_data.xml",
        "data/ack_in_exchange_type_data.xml",
        "data/ack_out_exchange_type_data.xml",
        "data/business_header_qweb_template.xml",
        "data/contact_details_qweb_template.xml",
        "views/res_partner.xml",
        "views/edi_backend.xml",
        "views/uom_uom.xml",
    ],
    "post_init_hook": "post_init_hook",
}
