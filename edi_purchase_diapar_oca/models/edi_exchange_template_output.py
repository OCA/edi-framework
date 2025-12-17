from odoo import fields, models


class EDIExchangeTemplateOutput(models.Model):
    _inherit = "edi.exchange.template.output"

    customer_code = fields.Char()
    constant_file_start = fields.Char()
    constant_file_end = fields.Char()
    vrp_code = fields.Char()
