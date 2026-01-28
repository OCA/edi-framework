# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
import email
import json
import logging
import re

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class EdiExchangeRecord(models.Model):
    _inherit = "edi.exchange.record"

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        record = super().message_new(
            msg_dict,
            custom_values=custom_values,
        )
        if record.type_id.direction != "input":
            raise UserError(_("Received email for non-incoming exchange type."))
        if record.type_id.mail_as_attachment:
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
            record._set_file_content(json.dumps(new_message_dict))
            record.edi_exchange_state = "input_received"
        else:
            content = False
            filename = False
            for attachment in msg_dict.get("attachments", []):
                if re.match(
                    record.type_id.exchange_filename_pattern or ".*",
                    attachment.fname,
                    re.IGNORECASE,
                ):
                    content = self._process_email_attachment(attachment)
                    filename = attachment.fname
                    break
            if content:
                record._set_file_content(content)
                record.exchange_filename = filename
                record.edi_exchange_state = "input_received"
        return record

    def _process_email_attachment(self, attachment):
        """Process email attachment to be stored as file content."""
        data = attachment[1]
        if isinstance(data, email.message.EmailMessage):
            data = data.as_bytes()
        if not isinstance(data, bytes):
            data = str(data).encode("utf-8")
        return base64.b64encode(data).decode("utf-8")
