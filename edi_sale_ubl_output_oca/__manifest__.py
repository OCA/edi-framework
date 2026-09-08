# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "EDI Sales",
    "summary": """
        Configuration and special behaviors for EDI on sales.
    """,
    "version": "18.0.1.3.1",
    "development_status": "Alpha",
    "license": "AGPL-3",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/edi-framework",
    "depends": [
        "edi_sale_ubl_oca",
        "edi_xml_oca",
        "edi_exchange_template_oca",
        "edi_exchange_template_party_data",
        "edi_ubl_output_base_oca",
        "edi_state_oca",
        # This is for the UBL schema
        "base_ubl",
        # This could be made optional
        # but the delivery part would need another source of data
        "sale_stock",
    ],
    "data": [
        "templates/qweb_tmpl_order_response.xml",
    ],
    "demo": [
        "demo/exc_templ_order_response.xml",
        "demo/edi_exchange_type.xml",
    ],
}
