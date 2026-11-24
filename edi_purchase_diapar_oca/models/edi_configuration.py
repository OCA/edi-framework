import datetime
import time

from odoo import api, models


class EDIConfiguration(models.Model):
    _inherit = "edi.configuration"

    @api.model
    def get_datenow_format_for_file(self):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        date = now.split(" ")[0].replace("-", "")
        hour = now.split(" ")[1].replace(":", "")
        return date, hour

    @api.model
    def get_datetime_format_ddmmyyyy(self, do_date):
        if not isinstance(do_date, datetime.datetime):
            do_date = datetime.datetime.strptime(do_date, "%Y-%m-%d %H:%M:%S")
        return "%02d%02d%s" % (
            do_date.day,
            do_date.month,
            str(do_date.year)[2:],
        )

    @api.model
    def get_date_format_yyyymmdd(self, date):
        """
        Transform a string date to datetime and format it to standard odoo
        date format
        """
        return datetime.datetime.strptime(date, "%y%m%d").strftime("%Y-%m-%d")

    @api.model
    def get_date_format_ble_yyyymmdd(self, date):
        """
        Transform a string date (specific to delivery order interface format)
        to datetime object and format it to standard odoo date format
        """
        return datetime.datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d")

    @api.model
    def insert_separator(self, string, index, separator):
        """
        This method is to insert a separator inside string on a certain
        position
        """
        return string[:index] + separator + string[index:]

    def _fix_lenght(self, value, lenght, mode="float", replace="", position="before"):
        value = str(value)
        if mode == "float":
            value = value.split(".")[0]
        if position == "before":
            value = "".join([replace for i in range(lenght - len(value))]) + value
        else:
            value += "".join([replace for i in range(lenght - len(value))])
        return value[0:lenght]
