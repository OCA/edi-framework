# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "custom_module",
    "summary": """
    Custom module
    """,
    "version": "14.0.1.0.0",
    "website": "https://github.com/OCA/edi",
    "development_status": "Beta",
    "license": "LGPL-3",
    "author": "ForgeFlow,Odoo Community Association (OCA)",
    "maintainers": ["MiquelRForgeFlow"],
    "depends": [
        "edi_oca",
    ],
    "data": [
        "security/ir_model_access.xml",
        "views/edi_backend_group_views.xml",
        "views/edi_backend_views.xml",
        "views/menuitems.xml",
    ],
}
