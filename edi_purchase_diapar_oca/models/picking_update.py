# Copyright (C) 2016-Today: Druidoo (<http://www.druidoo.net/>)
# @author: Druidoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html
from odoo import Command, fields, models


class PickingEdi(models.Model):
    _name = "picking.edi"
    _description = "Picking EDI"

    product_id = fields.Many2one("product.product")
    ordered_quantity = fields.Float()
    product_qty = fields.Float(string="EDI Quantity")
    package_qty = fields.Float(string="Product package")
    line_to_update_id = fields.Many2one("stock.move")
    picking_update_id = fields.Many2one("picking.update")


class PickingUpdate(models.Model):
    _name = "picking.update"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Picking Update"

    done = fields.Boolean(readonly=True)
    name = fields.Many2one("stock.picking", string="Order picking", readonly=True)
    values_proposed_ids = fields.One2many(
        "picking.edi",
        inverse_name="picking_update_id",
        string="Quantities to update",
        readonly=True,
    )

    def _prepare_values_proposed(self, proposition):
        self.ensure_one()
        return {
            "quantity": proposition.product_qty,
        }

    def button_update_picking_order(self):
        self.ensure_one()
        commands = []
        for proposition in self.values_proposed_ids:
            commands += [
                Command.update(
                    proposition.line_to_update_id.id,
                    self._prepare_values_proposed(proposition),
                )
            ]
        self.done = True
        self.name.write({"move_ids": commands})
        return True
