from odoo import fields, models


class EDIPriceMapping(models.Model):
    _name = "edi.field.mapping"
    _order = "position"
    _description = "EDI Price Mapping"

    sequence = fields.Integer(default=1)
    position = fields.Integer(required=True)
    exchange_type_id = fields.Many2one(
        comodel_name="edi.exchange.type",
        string="Exchange type",
        required=True,
    )
    mapping_field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Prices mapping field",
    )
    name = fields.Char(string="Zone description")
    sequence_start = fields.Integer()
    sequence_end = fields.Integer()
    is_numeric = fields.Boolean(string="Is numeric ?")
    is_date = fields.Boolean(string="Is a date?")
    decimal_precision = fields.Integer()
