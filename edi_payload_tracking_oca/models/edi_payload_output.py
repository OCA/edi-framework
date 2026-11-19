# Copyright 2026 Camptocamp SA
# @author Akim Juillerat <akim.juillerat@camptocamp.com>
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from psycopg2.errors import UniqueViolation

from odoo import api, fields, models
from odoo.tools import mute_logger


class EDIPayloadOutput(models.Model):
    """Payload last exported for a record, one per record."""

    _name = "edi.payload.output"
    _description = "EDI payload output"

    model_id = fields.Many2one(
        comodel_name="ir.model",
        required=True,
        index=True,
        ondelete="cascade",
    )
    res_id = fields.Integer(required=True, index=True)
    payload = fields.Json(default=dict)

    _record_uniq = models.Constraint(
        "unique(model_id, res_id)",
        "Only one exported payload is allowed per record.",
    )

    @api.model
    def _find_for_record(self, record):
        """Return the stored payload record of `record`, if any."""
        record.ensure_one()
        model = self.env["ir.model"]._get(record._name)
        return self.search(
            [
                ("model_id", "=", model.id),
                ("res_id", "=", record.id),
            ],
            limit=1,
        )

    @api.model
    def get_payload(self, record):
        """Return the payload stored for `record`, or an empty dict."""
        payload = self._find_for_record(record)
        return payload.payload or {}

    @api.model
    def set_payload(self, record, payload):
        """Store `payload` for `record`, replacing the previous one.

        When a concurrent transaction created the payload of the same record
        in the meantime, raise the error `_payload_concurrent_create_error()`
        returns. This transaction stays usable.
        """
        record.ensure_one()
        payload = payload or {}
        exported = self._find_for_record(record)
        if exported:
            exported.payload = payload
            return exported
        # Another transaction exporting the same record may have created its
        # payload after this one started, unseen by the lookup above.
        try:
            with self.env.cr.savepoint(), mute_logger("odoo.sql_db"):
                return self.create(
                    {
                        "model_id": self.env["ir.model"]._get_id(record._name),
                        "res_id": record.id,
                        "payload": payload,
                    }
                )
        except UniqueViolation as err:
            error = self._payload_concurrent_create_error(record, err)
            if error is err:
                raise
            raise error from err

    @api.model
    def _payload_concurrent_create_error(self, record, error):
        """Return the error to raise when `record`'s payload exists already.

        `error` is the `UniqueViolation` of the insert, returned by default.
        Override to raise another error, e.g. to retry the exporting job.
        """
        return error
