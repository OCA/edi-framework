# Copyright 2024 Camptocamp
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class EDIExchangeRecord(models.Model):

    _inherit = "edi.exchange.record"

    edi_exchange_state = fields.Selection(
        selection_add=[
            ("obsolete", "Obsolete"),
        ],
        ondelete={"obsolete": "cascade"},
    )
    block_obsolescence = fields.Boolean(
        default=False,
        help="Flag record that can never be marked as obsolete",
    )

    @api.constrains("edi_exchange_state")
    def _constrain_edi_exchange_state(self):
        # Remove `obsolete` record for this check
        self = self.filtered(lambda r: r.edi_exchange_state != "obsolete")
        return super()._constrain_edi_exchange_state()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            check_obsoleted_record = (
                rec.type_id.direction == "output" and rec.type_id.deduplicate_on_send
            )
            if check_obsoleted_record:
                obsoleted_records = rec._edi_get_duplicates()
                if obsoleted_records:
                    obsoleted_records.edi_exchange_state = "obsolete"
        return records

    def _edi_get_duplicates(self, count=None):
        self.ensure_one()
        older_duplicates = self.search(
            [
                ("id", "<", self.id),
                ("res_id", "=", self.res_id),
                ("model", "=", self.model),
                ("type_id", "=", self.type_id.id),
                ("edi_exchange_state", "in", ("new", "output_pending")),
                ("block_obsolescence", "=", False),
            ],
            count=count,
        )
        return older_duplicates
