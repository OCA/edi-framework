# Copyright 2026 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import new_test_user

from odoo.addons.edi_core_oca.models.edi_exchange_record import EDIExchangeRecord
from odoo.addons.edi_core_oca.tests.common import EDIBackendCommonTestCase


class EDIExchangeRecordFileManagerCommon(EDIBackendCommonTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Prepare 2 users w/ different access groups:
        # - user with access should have ``create``, ``read`` and ``write`` access on
        #   the wizard (see ``_user_has_file_manager_access()`` for the operations to
        #   check, and ``security/ir_model_access.xml`` for the group that grants them)
        # - user without access should not have those access rights, but should at least
        #   have ``read`` access on ``edi.exchange.record``
        # - both should be internal users
        xmlids = "base.group_user"
        cls.user_with_access = new_test_user(
            cls.env,
            login="user_with_access",
            groups=f"edi_core_oca.group_edi_override_exchange_file_content,{xmlids}",
        )
        cls.user_without_access = new_test_user(
            cls.env,
            login="user_without_access",
            groups=f"base_edi.group_edi_user,{xmlids}",
        )

    @classmethod
    def _create_record(
        cls,
        type_code: str,
        state: str,
        content: str | bytes = "a,b\n1,2\n",
        custom_values: dict | None = None,
    ) -> EDIExchangeRecord:
        """Creates an EDI Exchange Record

        :param type_code: the Exchange Type's code
        :param state: the Exchange Record's state
        :param content: the Exchange Record's file content (default: "a,b\n1,2\n")
        :param custom_values: additional values to set on the record
        """
        values = {
            "edi_exchange_state": state,
            "model": cls.partner._name,
            "res_id": cls.partner.id,
        }
        if custom_values:
            values.update(custom_values)
        record = cls.backend.create_record(type_code, values)
        if content:
            record._set_file_content(content)
        return record

    @classmethod
    def _create_wizard(
        cls,
        exchange_record: EDIExchangeRecord | None = None,
        custom_values: dict | None = None,
    ):
        """Creates an EDI Exchange Record File Manager wizard

        :param exchange_record: the Exchange Record to link; if none is provided, a
            new one is created with default values
        :param custom_values: additional values to set on the wizard
        """
        if exchange_record is None:
            exchange_record = cls._create_record(
                cls.exchange_type_in.code, "input_processed_error", content="Test"
            )
        values = exchange_record._prepare_file_manager_wizard_values()
        if custom_values:
            values.update(custom_values)
        return cls.env["edi.exchange.record.file.manager"].create(values)
