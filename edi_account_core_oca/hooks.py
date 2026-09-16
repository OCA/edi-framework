def pre_init_hook(env):
    # Update the module name in the database
    # This should happen only if we migrate from edi_oca to edi_core_oca
    env.cr.execute(
        """
        UPDATE ir_model_data
        SET module = 'edi_account_core_oca'
        WHERE module = 'edi_account_oca'
        """
    )
