# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def post_init_hook(env):
    """
    Hook used to init automatically some GS1 code on existing UoM
    :param env: Odoo Environment
    :return:
    """
    env["uom.uom"]._execute_gs1_map_code()
