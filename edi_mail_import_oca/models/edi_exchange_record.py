# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
import email
import json
import logging
import re
from collections import defaultdict

from odoo import api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class EdiExchangeRecord(models.Model):
    _inherit = "edi.exchange.record"

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        backend_id = custom_values.get("backend_id") if custom_values else None
        data = defaultdict(list)
        if backend_id and not custom_values.get("type_id"):
            backend = self.env["edi.backend"].browse(backend_id)
            types = self.env["edi.exchange.type"].search(
                backend._mail_exchange_type_pending_input_domain()
            )
            for exchange_type in types:
                if exchange_type.mail_record_policy == "pattern":
                    for attachment in msg_dict.get("attachments", []):
                        if re.match(
                            exchange_type.exchange_filename_pattern,
                            attachment.fname,
                            re.IGNORECASE,
                        ):
                            data[exchange_type.id].append(
                                [
                                    attachment.fname,
                                    self._process_email_attachment(attachment),
                                ]
                            )
                else:
                    new_message_dict = msg_dict.copy()
                    attachments = new_message_dict.pop("attachments", [])
                    new_message_dict["attachments"] = []
                    for attachment in attachments:
                        new_message_dict["attachments"].append(
                            {
                                "info": attachment.info,
                                "data": self._process_email_attachment(attachment),
                                "fname": attachment.fname,
                            }
                        )
                    data[exchange_type.id].append(
                        ["email_message.json", json.dumps(new_message_dict)]
                    )
        if (not custom_values or "type_id" not in custom_values) and not data:
            raise UserError(
                self.env._(
                    "No exchange type found for incoming email with subject '%s'",
                    msg_dict.get("subject"),
                )
            )
        if data:
            for exchange_type_id in data:
                filename, content = data[exchange_type_id].pop()
                custom_values["type_id"] = exchange_type_id
                break
        record = super().message_new(
            msg_dict,
            custom_values=custom_values,
        )
        if data:
            record._set_file_content(content)
            record.exchange_filename = filename
            record.edi_exchange_state = "input_received"
        for exchange_type_id in data:
            for filename, content in data[exchange_type_id]:
                new_record = record.copy(
                    default={
                        "type_id": exchange_type_id,
                    }
                )
                new_record._set_file_content(content)
                new_record.exchange_filename = filename
                new_record.edi_exchange_state = "input_received"
        return record

    @api.model
    def _process_email_attachment(self, attachment):
        """Process email attachment to be stored as file content."""
        data = attachment[1]
        if isinstance(data, email.message.EmailMessage):
            data = data.as_bytes()
        if not isinstance(data, bytes):
            data = str(data).encode("utf-8")
        return base64.b64encode(data).decode("utf-8")
