# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json

from odoo.addons.mail.tests.common import MailCommon
from odoo.addons.test_mail.data.test_mail_data import MAIL_EML_ATTACHMENT


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
                "alias_name": "edi-input",
            }
        )
        cls.exchange_type_01 = cls.env["edi.exchange.type"].create(
            {
                "name": "Test Exchange Type",
                "code": "test_exchange_type_01",
                "mail_record_policy": "full",
                "direction": "input",
                "backend_type_id": cls.backend_type.id,
                "backend_id": cls.backend.id,
                "process_model_id": cls.env.ref("base.model_res_partner").id,
            }
        )
        cls.exchange_type_02 = cls.env["edi.exchange.type"].create(
            {
                "name": "Test Exchange Type",
                "code": "test_exchange_type_02",
                "mail_record_policy": "pattern",
                "exchange_filename_pattern": ".*eml",
                "direction": "input",
                "backend_type_id": cls.backend_type.id,
                "backend_id": cls.backend.id,
                "process_model_id": cls.env.ref("base.model_res_partner").id,
            }
        )
        cls.exchange_type_03 = cls.env["edi.exchange.type"].create(
            {
                "name": "Test Exchange Type",
                "code": "test_exchange_type_03",
                "mail_record_policy": "pattern",
                "exchange_filename_pattern": ".*jpg",
                "direction": "input",
                "backend_type_id": cls.backend_type.id,
                "backend_id": cls.backend.id,
                "process_model_id": cls.env.ref("base.model_res_partner").id,
            }
        )
        cls.exchange_type_04 = cls.env["edi.exchange.type"].create(
            {
                "name": "Test Exchange Type",
                "code": "test_exchange_type_04",
                "exchange_filename_pattern": ".*eml",
                "direction": "input",
                "backend_type_id": cls.backend_type.id,
                "backend_id": cls.backend.id,
                "process_model_id": cls.env.ref("base.model_res_partner").id,
            }
        )
        cls.exchange_types = (
            cls.exchange_type_01 | cls.exchange_type_02 | cls.exchange_type_03
        )

    def test_import_full(self):
        self.assertTrue(self.backend.alias_email)
        self.assertFalse(
            self.env["edi.exchange.record"].search(
                [
                    ("type_id", "in", self.exchange_types.ids),
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
        self.env["mail.thread"].message_process("mail.thread", mail)
        record = self.env["edi.exchange.record"].search(
            [
                ("type_id", "=", self.exchange_type_01.id),
            ]
        )
        self.assertTrue(record)
        self.assertEqual(record.edi_exchange_state, "input_received")
        file_content = record._get_file_content()
        self.assertTrue(file_content)
        data = json.loads(file_content)
        self.assertIn("body", data)
        record = self.env["edi.exchange.record"].search(
            [
                ("type_id", "=", self.exchange_type_02.id),
            ]
        )
        self.assertTrue(record)
        self.assertEqual(record.edi_exchange_state, "input_received")
        self.assertEqual(record.exchange_filename, "original_msg.eml")
        self.assertFalse(
            self.env["edi.exchange.record"].search(
                [
                    ("type_id", "=", self.exchange_type_03.id),
                ]
            )
        )
        self.assertFalse(
            self.env["edi.exchange.record"].search(
                [
                    ("type_id", "=", self.exchange_type_04.id),
                ]
            )
        )
