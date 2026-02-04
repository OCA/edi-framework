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

    def _message_new_prepare_data(self, msg_dict, custom_values=None):
        """Prepare incoming email files for their matching exchange types.

        Exchange types with the ``pattern`` mail policy receive each
        attachment whose filename matches their configured pattern. All
        other types receive the complete message serialized as JSON, with
        attachment data encoded for storage. The first prepared file is
        reserved for the new exchange record; additional files remain in the
        mapping for creation as separate records.

        :param msg_dict: Parsed incoming email data, including its
            attachments.
        :param custom_values: Values for the new exchange record. The
            ``backend_id`` selects its backend; an optional ``type_id``
            restricts processing to that exchange type. When ``type_id`` is
            absent, it is set to the type of the first prepared file.
        :return: A tuple containing the remaining files, updated custom
            values, and the first file's filename and content. Remaining
            files are represented as a mapping from exchange type IDs to
            lists of ``[filename, content]`` pairs. Raises :class:`UserError`
            if no exchange type produces a file.
        """
        if custom_values is None:
            custom_values = {}
        backend_id = custom_values.get("backend_id")
        data = defaultdict(list)
        filename = None
        content = None
        if backend_id:
            backend = self.env["edi.backend"].browse(backend_id)
            if type_id := custom_values.get("type_id"):
                types = self.env["edi.exchange.type"].browse(type_id)
            else:
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
        if custom_values.get("type_id") and custom_values["type_id"] not in data:
            raise UserError(
                self.env._(
                    "The exchange type '%(type_id)s' for incoming email with subject "
                    "'%(subject)s' did not return any data",
                    type_id=custom_values["type_id"],
                    subject=msg_dict.get("subject"),
                )
            )
        if not data:
            raise UserError(
                self.env._(
                    "No exchange type found for incoming email with subject '%s'",
                    msg_dict.get("subject"),
                )
            )
        for exchange_type_id in data:
            filename, content = data[exchange_type_id].pop()
            if "type_id" not in custom_values:
                custom_values["type_id"] = exchange_type_id
            break
        return data, custom_values, filename, content

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        data, custom_values, filename, content = self._message_new_prepare_data(
            msg_dict, custom_values
        )
        record = super().message_new(
            msg_dict,
            custom_values=custom_values,
        )
        # Content and Filename correspond to the main exchange type (or the first one)
        # of the email message.
        # Other data will be processed as additional exchange records to process.
        if content and filename:
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
