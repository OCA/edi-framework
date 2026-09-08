# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class EDIExchangeType(models.Model):
    _inherit = "edi.exchange.type"

    deduplicate_on_exchange = fields.Boolean(
        string="Deduplicate on Exchange",
        default=False,
        help="When an exchange record is created, mark the older ones for the "
        "same record that are still pending as obsolete, so only the freshest "
        "one is sent or processed. Records without a related record match on "
        "the exchange type alone, which suits full-dump payloads where only "
        "the latest one matters.",
    )
    # Kept for backwards compatibility.
    # TODO: Remove this alias in 20.0 migration
    deduplicate_on_send = fields.Boolean(
        string="Deduplicate on Send",
        compute="_compute_deduplicate_on_send",
        inverse="_inverse_deduplicate_on_send",
        search="_search_deduplicate_on_send",
        help="Deprecated: alias of 'Deduplicate on Exchange'.",
    )
    delete_obsolete_records = fields.Boolean(
        string="Delete obsolete records",
        default=True,
        help="Delete records marked as obsolete.",
    )

    deduplicate_on_exchange_record_status = fields.Char(
        default="new,output_pending,input_pending,input_received",
        groups="base.group_no_one",
    )

    @api.depends("deduplicate_on_exchange")
    def _compute_deduplicate_on_send(self):
        for rec in self:
            rec.deduplicate_on_send = rec.deduplicate_on_exchange

    def _inverse_deduplicate_on_send(self):
        _logger.warning(
            "'deduplicate_on_send' is deprecated on edi.exchange.type %s, "
            "use 'deduplicate_on_exchange' instead.",
            ", ".join(self.mapped("code")),
        )
        for rec in self:
            rec.deduplicate_on_exchange = rec.deduplicate_on_send

    def _search_deduplicate_on_send(self, operator, value):
        return [("deduplicate_on_exchange", operator, value)]

    def _deduplicate_get_exchange_record_states(self):
        self.ensure_one()
        configured_states = self.sudo().deduplicate_on_exchange_record_status or ""
        return {
            state.strip() for state in configured_states.split(",") if state.strip()
        }

    @api.constrains("deduplicate_on_exchange_record_status")
    def _check_deduplicate_on_exchange_record_status(self):
        exchange_state_field = self.env["edi.exchange.record"]._fields[
            "edi_exchange_state"
        ]
        allowed_states = set(exchange_state_field.get_values(self.env))
        for rec in self:
            configured_states = rec._deduplicate_get_exchange_record_states()
            invalid_states = sorted(configured_states - allowed_states)
            if invalid_states:
                raise ValidationError(
                    self.env._(
                        "Invalid exchange state(s): %(invalid_states)s. "
                        "Allowed values are: %(allowed_states)s",
                        invalid_states=", ".join(invalid_states),
                        allowed_states=", ".join(sorted(allowed_states)),
                    )
                )
