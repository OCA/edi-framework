from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_assign(self, force_qty=False):
        res = super()._action_assign(force_qty=force_qty)
        if self.env.context.get("qty_from_file_policy"):
            # Set the quantity to 0 and it will be updated later in the process.
            self.quantity = 0
        return res
