# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# @author: Lois Rilo <lois.rilo@forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "EDI Invoice Import UBL Endpoint Example",
    "summary": "Provide a default endpoint to import Invoices in UBL format.",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/edi",
    "author": "ForgeFlow,Odoo Community Association (OCA)",
    "maintainers": ["LoisRForgeFlow"],
    "depends": [
        "edi_account_invoice_import",
        "account_invoice_import_ubl",
        "edi_account_invoice_import_ubl",
        "edi_endpoint_oca",
    ],
    "auto_install": False,
    "data": ["data/endpoint.xml"],
}
