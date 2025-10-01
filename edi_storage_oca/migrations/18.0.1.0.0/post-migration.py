from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    model = env.ref("edi_storage_oca.model_edi_oca_storage_handler")
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE edi_exchange_type
        SET send_model_id = { model.id }
        WHERE direction = 'output'
          AND send_model_id IS NULL
          AND EXISTS (
              SELECT 1
              FROM edi_backend
              WHERE (
                edi_backend.id = edi_exchange_type.backend_id
                OR (
                  edi_exchange_type.backend_id IS NULL
                  AND edi_backend.backend_type_id = edi_exchange_type.backend_type_id
                )
                AND edi_backend.active IS TRUE
              )
            )
            """,
    )
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE edi_exchange_type
        SET receive_model_id = {model.id}
        WHERE direction = 'input'
          AND receive_model_id IS NULL
          AND EXISTS (
              SELECT 1
              FROM edi_backend
              WHERE (
                edi_backend.id = edi_exchange_type.backend_id
                OR (
                  edi_exchange_type.backend_id IS NULL
                  AND edi_backend.backend_type_id = edi_exchange_type.backend_type_id
                )
                AND edi_backend.active IS TRUE
            )
            """,
    )
