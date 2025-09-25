# Copyright 2025 Dixmit
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Edi Queue Oca",
    "summary": """Set Queue Jobs on EDI""",
    "version": "18.0.1.0.1",
    "license": "LGPL-3",
    "author": "Dixmit,Camptocamp,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/edi-framework",
    "depends": ["edi_core_oca", "queue_job"],
    "data": [
        "views/edi_exchange_type.xml",
        "security/ir_model_access.xml",
        "data/job_channel.xml",
        "data/job_function.xml",
        "views/edi_exchange_record.xml",
    ],
    "demo": [],
}
