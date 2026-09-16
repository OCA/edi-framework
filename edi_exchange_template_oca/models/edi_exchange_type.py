# Copyright 2025 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import api, exceptions, fields, models


class EDIExchangeType(models.Model):
    _inherit = "edi.exchange.type"

    output_template_id = fields.Many2one(
        comodel_name="edi.exchange.template.output",
        string="Exchange Template",
        ondelete="restrict",
        required=False,
        help="Template used to generate or process this type.",
    )
    output_template_allowed_ids = fields.Many2many(
        comodel_name="edi.exchange.template.output",
        # Inverse relation is defined in `edi.exchange.template.mixin`
        relation="edi_exchange_template_type_rel",
        column1="type_id",
        column2="template_id",
        string="Allowed Templates",
        help="Templates allowed to be used with this type.",
    )

    @api.constrains("output_template_id")
    def _check_output_template_id(self):
        for rec in self:
            tmpl = rec.output_template_id
            if (
                tmpl
                and tmpl.allowed_type_ids
                and tmpl not in rec.output_template_allowed_ids
            ):
                raise exceptions.ValidationError(
                    self.env._("Template not allowed for this type.")
                )
