# Copyright 2023 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import _, api, exceptions, fields, models


class EDIState(models.Model):
    """EDI specific state."""

    _name = "edi.state"
    _description = __doc__

    name = fields.Char(translate=True, required=True)
    description = fields.Char(translate=True)
    code = fields.Char()
    workflow_id = fields.Many2one(
        comodel_name="edi.state.workflow",
        ondelete="cascade",
    )
    is_default = fields.Boolean()

    _sql_constraints = [
        (
            "state_workflow_code_uniq",
            "unique(code, workflow_id)",
            "Code must be unique per each workflow.",
        )
    ]

    @api.constrains("is_default")
    def _check_is_default(self):
        self.ensure_one()
        for rec in self:
            if (
                self.search_count(
                    [
                        ("workflow_id", "=", rec.workflow_id.id),
                        ("is_default", "=", True),
                    ]
                )
                > 1
            ):
                raise exceptions.ValidationError(
                    _("Only one state per workflow can be the default one.")
                )
