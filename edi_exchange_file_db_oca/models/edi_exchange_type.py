# Copyright 2026 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models

MAX_SIZE_PARAM = "edi_exchange_file_db_oca.max_size_kb"


class EDIExchangeType(models.Model):
    _inherit = "edi.exchange.type"

    store_file_content_in_db = fields.Boolean(
        string="Store File Content in Database",
        default=True,
        help="Keep the content of the exchange files of this type in the "
        "database instead of the filestore. The file is still an attachment "
        "of the exchange record: only the place where the attachment keeps "
        "its content changes, so a database restored without its filestore "
        "still holds it.",
    )
    file_content_db_max_size = fields.Integer(
        string="Max File Content Size in Database (KB)",
        help="Files whose content is bigger than this size keep it in the "
        "filestore. 0 uses the global limit, set in the system parameter "
        "'edi_exchange_file_db_oca.max_size_kb' (no limit when it is not set).",
    )

    @api.model
    def _get_file_content_db_global_max_size(self):
        value = self.env["ir.config_parameter"].sudo().get_param(MAX_SIZE_PARAM)
        try:
            return int(value or 0)
        except ValueError:
            return 0

    def _get_file_content_db_max_size(self):
        self.ensure_one()
        return (
            self.file_content_db_max_size or self._get_file_content_db_global_max_size()
        )

    def _should_store_file_content_in_db(self, size):
        if not self:
            return False
        self.ensure_one()
        if not self.store_file_content_in_db:
            return False
        max_size = self._get_file_content_db_max_size()
        return not max_size or size <= max_size * 1024
