# Copyright 2024 Camptocamp
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.fields import Domain


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

    @api.autovacuum
    def _gc_delete_obsolete_records(self):
        """Delete the obsolete records, oldest first, in batches of 1000.

        Called from the base autovacuum cron, which commits after each batch
        and calls it again while it returns remaining records.
        """
        limit = 1000
        records = self.search(
            self._obsolete_records_domain(),
            order="create_date",
            limit=limit + 1,
        )
        records[:limit].sudo().unlink()
        return len(records[:limit]), len(records) > limit

    @api.model
    def _obsolete_records_domain(self):
        """Domain of the obsolete records the autovacuum deletes."""
        return Domain("edi_exchange_state", "=", "obsolete") & Domain(
            "type_id.delete_obsolete_records", "=", True
        )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.type_id.deduplicate_on_exchange:
                obsoleted_records = rec._edi_get_duplicates()
                if obsoleted_records:
                    obsoleted_records.edi_exchange_state = "obsolete"
        return records

    def _edi_get_duplicates(self, count=False):
        self.ensure_one()
        edi_exchange_state_to_check = list(
            self.type_id._deduplicate_get_exchange_record_states()
        )
        return (self.search_count if count else self.search)(
            Domain(
                [
                    ("id", "<", self.id),
                    ("res_id", "=", self.res_id),
                    ("model", "=", self.model),
                    ("type_id", "=", self.type_id.id),
                    ("edi_exchange_state", "in", edi_exchange_state_to_check),
                    ("block_obsolescence", "=", False),
                ],
            )
        )
