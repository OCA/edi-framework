# Copyright 2025 ForgeFlow
# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    edi_stock_picking_conf_ids = fields.Many2many(
        string="EDI stock configuration",
        comodel_name="edi.configuration",
        relation="res_partner_edi_stock_picking_configuration_rel",
        column1="partner_id",
        column2="conf_id",
        domain=[("model_name", "=", "stock.picking")],
    )
