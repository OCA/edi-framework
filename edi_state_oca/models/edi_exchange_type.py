# Copyright 2023 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, exceptions, fields, models


class EDIExchangeType(models.Model):

    _inherit = "edi.exchange.type"

    state_workflow_ids = fields.Many2many(
        string="Enabled state workflows",
        comodel_name="edi.state.workflow",
        help=(
            "Allowed workflows that can be used by this type of exchanges. "
            "You can select only 1 workflow per model."
        ),
    )

    @api.constrains("state_workflow_ids")
    def _check_workflow_models(self):
        for rec in self:
            models = [x.model_id.id for x in rec.state_workflow_ids]
            if any([(models.count(x) > 1) for x in models]):
                raise exceptions.UserError(_("Only one workflow per model is allowed"))

    def get_state_for_model(self, model, code=None, default=False):
        assert code or default
        wf = self.state_workflow_ids.filtered(lambda x: x.model_id.model == model)
        return wf.get_state(code) if code else wf.get_default_state()
