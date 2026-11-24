from datetime import datetime

from pytz import timezone, utc

from odoo import fields, models

DEFAULT_DATE_FMT = "%Y%m%d"
DEFAULT_TIME_FMT = "%H%M%S"


class EDIExchangeType(models.Model):
    _inherit = "edi.exchange.type"

    field_mapping_ids = fields.One2many(
        comodel_name="edi.field.mapping",
        inverse_name="exchange_type_id",
        string="Field Mappings",
    )
    header_code = fields.Char()
    lines_code = fields.Char()
    delivery_sign = fields.Char()

    def _make_exchange_filename_time(self):
        self.ensure_one()
        pattern_settings = self.advanced_settings.get("filename_pattern", {})
        force_tz = pattern_settings.get("force_tz", self.env.user.tz)
        time_pattern = pattern_settings.get("time_pattern", DEFAULT_TIME_FMT)
        tz = timezone(force_tz) if force_tz else None
        now = datetime.now(utc).astimezone(tz)
        return self.env["ir.http"]._slugify(now.strftime(time_pattern))

    def _make_exchange_filename(self, exchange_record):
        pattern = self.exchange_filename_pattern
        if "{time}" in pattern:
            ext = self.exchange_file_ext
            if ext:
                pattern += ".{ext}"
            dt = self._make_exchange_filename_datetime()
            seq = self._make_exchange_filename_sequence()
            record_name = self._get_record_name(exchange_record)
            record = exchange_record
            if exchange_record.model and exchange_record.res_id:
                record = exchange_record.record
            return pattern.format(
                exchange_record=exchange_record,
                record=record,
                record_name=record_name,
                type=self,
                dt=dt,
                seq=seq,
                ext=ext,
                time=self._make_exchange_filename_time(),
            )
        return super()._make_exchange_filename(exchange_record)
