# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json

from odoo.tests import tagged

from odoo.addons.mail.tests.common import MailCommon
from odoo.addons.test_mail.data.test_mail_data import MAIL_EML_ATTACHMENT


@tagged("mail_gateway")
class TestEmailParsing(MailCommon):
    """Test email parsing and import via mail gateway"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend_type = cls.env["edi.backend.type"].create(
            {
                "name": "Mail Import OCA Test Backend Type",
                "code": "mail_import_oca_test_backend_type",
            }
        )
        cls.backend = cls.env["edi.backend"].create(
            {
                "name": "Mail Import OCA Test Backend",
                "backend_type_id": cls.backend_type.id,
            }
        )
        cls.exchange_type = cls.env["edi.exchange.type"].create(
            {
                "name": "Test Exchange Type",
                "code": "test_exchange_type",
                "direction": "input",
                "alias_name": "edi-input",
                "backend_type_id": cls.backend_type.id,
                "backend_id": cls.backend.id,
            }
        )

    def test_import_full(self):
        self.assertTrue(self.exchange_type.alias_email)
        self.exchange_type.mail_as_attachment = True
        self.assertFalse(
            self.env["edi.exchange.record"].search(
                [
                    ("type_id", "=", self.exchange_type.id),
                ]
            )
        )
        mail = self.format(
            MAIL_EML_ATTACHMENT,
            to=self.exchange_type.alias_email,
            subject="purchase test mail",
            target_model="account.move",
            msg_id="<test-account-move-alias-id>",
        )
        self.env["mail.thread"].message_process("mail.thread", mail)
        record = self.env["edi.exchange.record"].search(
            [
                ("type_id", "=", self.exchange_type.id),
            ]
        )
        self.assertTrue(record)
        self.assertEqual(record.edi_exchange_state, "input_received")
        file_content = record._get_file_content()
        self.assertTrue(file_content)
        data = json.loads(file_content)
        self.assertIn("body", data)

    def test_import_specific_file(self):
        self.assertTrue(self.exchange_type.alias_email)
        self.exchange_type.mail_as_attachment = False
        self.exchange_type.exchange_filename_pattern = ".*eml"
        self.assertFalse(
            self.env["edi.exchange.record"].search(
                [
                    ("type_id", "=", self.exchange_type.id),
                ]
            )
        )
        mail = self.format(
            MAIL_EML_ATTACHMENT,
            to=self.exchange_type.alias_email,
            subject="purchase test mail",
            target_model="account.move",
            msg_id="<test-account-move-alias-id>",
        )
        self.env["mail.thread"].message_process("mail.thread", mail)
        record = self.env["edi.exchange.record"].search(
            [
                ("type_id", "=", self.exchange_type.id),
            ]
        )
        self.assertTrue(record)
        self.assertEqual(record.edi_exchange_state, "input_received")
        self.assertEqual(record.exchange_filename, "original_msg.eml")

    def test_import_no_file_found(self):
        self.assertTrue(self.exchange_type.alias_email)
        self.exchange_type.mail_as_attachment = False
        self.exchange_type.exchange_filename_pattern = ".*xml"
        self.assertFalse(
            self.env["edi.exchange.record"].search(
                [
                    ("type_id", "=", self.exchange_type.id),
                ]
            )
        )
        mail = self.format(
            MAIL_EML_ATTACHMENT,
            to=self.exchange_type.alias_email,
            subject="purchase test mail",
            target_model="account.move",
            msg_id="<test-account-move-alias-id>",
        )
        self.env["mail.thread"].message_process("mail.thread", mail)
        record = self.env["edi.exchange.record"].search(
            [
                ("type_id", "=", self.exchange_type.id),
            ]
        )
        self.assertTrue(record)
        self.assertEqual(record.edi_exchange_state, "new")
