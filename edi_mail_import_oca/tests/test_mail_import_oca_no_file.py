# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api
from odoo.exceptions import UserError
from odoo.tools import mute_logger

from odoo.addons.mail.tests.common import MailCommon
from odoo.addons.test_mail.data.test_mail_data import MAIL_EML_ATTACHMENT


class TestEmailParsing(MailCommon):
    """Test email parsing and import via mail gateway"""

    def setUp(self):
        super().setUp()
        self.registry_enter_test_mode()
        # now we make a test cursor for self.cr
        self.cr = self.registry.cursor()
        self.addCleanup(self.cr.close)
        self.env = api.Environment(self.cr, api.SUPERUSER_ID, {})
        self.backend_type = self.env["edi.backend.type"].create(
            {
                "name": "Mail Import OCA Test Backend Type",
                "code": "mail_import_oca_test_backend_type",
            }
        )
        self.backend = self.env["edi.backend"].create(
            {
                "name": "Mail Import OCA Test Backend",
                "backend_type_id": self.backend_type.id,
                "alias_name": "edi-input",
            }
        )
        self.exchange_type = self.env["edi.exchange.type"].create(
            {
                "name": "Test Exchange Type",
                "code": "test_exchange_type",
                "direction": "input",
                "mail_record_policy": "pattern",
                "exchange_filename_pattern": ".*xml",
                "backend_type_id": self.backend_type.id,
                "backend_id": self.backend.id,
                "process_model_id": self.env.ref("base.model_res_partner").id,
            }
        )

    @mute_logger("odoo.addons.edi_mail_import_oca.models.edi_exchange_record")
    def test_import_no_file_found(self):
        self.assertTrue(self.backend.alias_email)
        self.assertFalse(
            self.env["edi.exchange.record"].search(
                [
                    ("type_id", "=", self.exchange_type.id),
                ]
            )
        )
        mail = self.format(
            MAIL_EML_ATTACHMENT,
            to=self.backend.alias_email,
            subject="purchase test mail",
            target_model="account.move",
            msg_id="<test-account-move-alias-id>",
        )
        with self.assertRaises(UserError):
            self.env["mail.thread"].message_process("mail.thread", mail)
