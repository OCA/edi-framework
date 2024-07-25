# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class EDIExchangeType(models.Model):
    _inherit = "edi.exchange.type"

    edi_source_id = fields.Many2one(
        "utm.source",
        default=lambda self: self._default_edi_source_id(),
        help="The UTM Source to be used by this type of exchanges.",
    )

    @api.model
    def _default_edi_source_id(self):
        return self.env.ref(
            "edi_utm_oca.utm_source_edi",
            raise_if_not_found=False,
        )
