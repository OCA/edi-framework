# Copyright 2026 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class EDIExchangeRecord(models.Model):
    _inherit = "edi.exchange.record"

    button_open_file_manager_invisible = fields.Boolean(
        compute="_compute_button_open_file_manager_invisible"
    )

    def _can_use_file_manager(self) -> bool:
        """Returns True if the file manager wizard can be used for the current record

        By default, the file manager is available if:
        - the record contains a file
        - its state is either "Sent and Error" or "Error on Process"
        - current user is in group "EDI Override Exchange File Content"
        """
        self.ensure_one()
        allowed_states = self._get_file_manager_allowed_states()
        group_specs = ",".join(self._get_file_manager_allowed_groups_xmlids())
        return (
            bool(self.exchange_file)
            and self.edi_exchange_state in allowed_states
            and self.env.user.has_groups(group_specs)
        )

    @api.model
    def _get_file_manager_allowed_states(self) -> list[str]:
        """Returns the states allowing the file manager wizard to be displayed

        By default, returns "Sent and Error" and "Error on Process"
        """
        return ["output_sent_and_error", "input_processed_error"]

    @api.model
    def _get_file_manager_allowed_groups_xmlids(self) -> list[str]:
        """Returns the ``res.groups`` XMLIDs that allow users to see the button

        The list will be then aggregated with ``",".join()`` and passed as argument to
        ``self.env.user.has_groups()``.

        :returns: list of fully-qualified group XMLIDs, optionally preceded by ``!``,
            e.g.: ``["base.group_user", "base.group_portal", "!base.group_system"]``
        """
        return ["edi_core_oca.group_edi_override_exchange_file_content"]

    @api.depends("exchange_file", "edi_exchange_state")
    @api.depends_context("uid")
    def _compute_button_open_file_manager_invisible(self):
        """Computes whether the button to open the file manager should be invisible"""
        for rec in self:
            rec.button_open_file_manager_invisible = not rec._can_use_file_manager()

    def button_open_file_manager(self):
        """Prepares the file manager wizard and opens it"""
        self.ensure_one()
        self._check_can_use_file_manager()
        wizard = self.env["edi.exchange.record.file.manager"]
        return wizard.create([{"exchange_record_id": self.id}]).open()

    def _check_can_use_file_manager(self):
        """Raise if the file of the exchange cannot be managed from the wizard."""
        self.ensure_one()
        if not self._can_use_file_manager():
            raise UserError(self.env._("The file manager cannot be used now."))

    def _prepare_file_manager_wizard_values(self) -> api.ValuesType:
        """Prepares the values to create the file manager wizard"""
        self.ensure_one()
        return {"exchange_record_id": self.id}
