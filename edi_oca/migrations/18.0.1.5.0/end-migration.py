# Copyright 2025 Dixmit
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """
    Fill existing exchange types with the component model if not set.
    It is done after all the modules have been updated just for security reasons.
    """
    model = env.ref(
        "edi_component_oca.model_edi_oca_component_handler", raise_if_not_found=False
    )
    if not model:
        # If the model is not loaded, we don't have components to handle
        return
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE edi_exchange_type
        SET generate_model_id = %s
        WHERE generate_model_id IS NULL
        AND direction = 'output'
        """,
        (model.id,),
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE edi_exchange_type
        SET send_model_id = %s
        WHERE send_model_id IS NULL
        AND direction = 'output'
        """,
        (model.id,),
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE edi_exchange_type
        SET output_validate_model_id = %s
        WHERE output_validate_model_id IS NULL
        AND direction = 'output'
        """,
        (model.id,),
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE edi_exchange_type
        SET receive_model_id = %s
        WHERE receive_model_id IS NULL
        AND direction = 'input'
        """,
        (model.id,),
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE edi_exchange_type
        SET process_model_id = %s
        WHERE process_model_id IS NULL
        AND direction = 'input'
        """,
        (model.id,),
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE edi_exchange_type
        SET input_validate_model_id = %s
        WHERE input_validate_model_id IS NULL
        AND direction = 'input'
        """,
        (model.id,),
    )
