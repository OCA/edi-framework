# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


def post_init_hook(env):
    env["edi.exchange.type"].with_context(active_test=False).search(
        []
    )._create_default_notification_rules()
