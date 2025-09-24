# Copyright 2025 Camptocamp SA (http://www.camptocamp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade


@openupgrade.migrate
def migrate(env, version):
    env["edi.exchange.type"].search(
        [
            ("direction", "=", "output"),
            ("output_template_id", "!=", False),
        ]
    ).write(
        {
            "generate_model_id": env.ref(
                "edi_exchange_template_oca.model_edi_oca_template_handler"
            ).id
        }
    )
    for exchange_type in env["edi.exchange.type"].search(
        [
            ("direction", "=", "output"),
            ("generate_model_id", "=", False),
        ]
    ):
        if env["edi.exchange.template.output"].search(
            [
                ("backend_type_id", "=", exchange_type.backend_type_id.id),
                "|",
                ("allowed_type_ids", "=", exchange_type.id),
                ("allowed_type_ids", "=", False),
            ]
        ):
            exchange_type.generate_model_id = env.ref(
                "edi_exchange_template_oca.model_edi_oca_template_handler"
            )
