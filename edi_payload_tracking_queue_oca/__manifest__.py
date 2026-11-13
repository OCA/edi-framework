# Copyright 2026 Camptocamp SA
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "EDI Payload Tracking Queue",
    "summary": "Retry the job when a payload is stored concurrently",
    "version": "19.0.1.0.0",
    "category": "EDI",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/edi-framework",
    "license": "LGPL-3",
    "maintainers": ["simahawk"],
    "depends": [
        "edi_payload_tracking_oca",
        "edi_queue_oca",
    ],
    "auto_install": True,
}
