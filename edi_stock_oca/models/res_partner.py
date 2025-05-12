from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    edi_stock_picking_conf_ids = fields.Many2many(
        string="EDI sale configuration",
        comodel_name="edi.configuration",
        relation="res_partner_edi_stock_picking_configuration_rel",
        column1="partner_id",
        column2="conf_id",
        domain=[("model_name", "=", "stock.picking")],
    )
