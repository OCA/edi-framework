# Copyright 2023 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models


class EDIStateWorkflow(models.Model):
    """EDI state workflow."""

    _name = "edi.state.workflow"
    _description = __doc__

    name = fields.Char(required=True)
    description = fields.Char()
    backend_type_id = fields.Many2one(
        string="Backend type",
        comodel_name="edi.backend.type",
        required=True,
        ondelete="restrict",
    )
    state_ids = fields.One2many(
        string="Available states",
        comodel_name="edi.state",
        inverse_name="workflow_id",
    )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        ondelete="set null",
    )

    def is_valid_for_model(self, model_name):
        return self.model_id.model == model_name

    def get_default_state(self):
        return self.state_ids.filtered(lambda x: x.is_default)

    def get_state(self, code):
        return self.state_ids.filtered(lambda x: x.code == code)
