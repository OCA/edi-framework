# Copyright 2026 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from itertools import product

from lxml import etree

from odoo.exceptions import UserError
from odoo.tests.common import RecordCapturer as RC
from odoo.tests.common import users

from odoo.addons.base.models.res_users import Users

from .common import EDIExchangeRecordFileManagerCommon


class TestEDIExchangeRecord(EDIExchangeRecordFileManagerCommon):
    def _get_test_contents(self) -> list[str]:
        return ["", "test"]

    def _get_test_states(self) -> list[str]:
        state_field = self.env["edi.exchange.record"]._fields["edi_exchange_state"]
        return [v for v, __ in state_field._description_selection(self.env)]

    def _get_test_users(self) -> Users:
        return self.user_with_access + self.user_without_access

    @users("user_with_access", "user_without_access")
    def test_button_in_form_view(self):
        """Ensures button is correctly rendered, even for users without access"""
        view = self.env["edi.exchange.record"].get_view(view_type="form")
        arch = etree.fromstring(view["arch"])
        buttons = arch.xpath("//header/button[@name='button_open_file_manager']")
        self.assertTrue(buttons)
        self.assertTrue(
            all(
                b.get("invisible") == "button_open_file_manager_invisible"
                for b in buttons
            )
        )

    def test_compute_button_open_file_manager_visibility(self):
        """Ensures button visibility is correctly computed"""
        test_users = self._get_test_users()
        states = self._get_test_states()
        contents = self._get_test_contents()
        type_code = "test_csv_{}"
        for state, content in product(states, contents):
            # Create the record in ``sudo()`` (the test user is, by default, sys admin)
            # and then check what happens when ``button_open_file_manager_invisible`` is
            # computed for 2 different users (w/ and w/o access to the wizard)
            direction = "input" if state.startswith("input") else "output"
            rec = self._create_record(type_code.format(direction), state, content)
            for user in test_users:
                with self.subTest(user=user.login, state=state, content=content):
                    rec = rec.with_user(user)
                    self.assertEqual(
                        rec.button_open_file_manager_invisible,
                        not rec._can_use_file_manager(),
                    )

    def test_button_open_file_manager(self):
        """Ensures button method can be used only under proper conditions"""
        test_users = self._get_test_users()
        states = self._get_test_states()
        contents = self._get_test_contents()
        type_code = "test_csv_{}"
        for state, content in product(states, contents):
            # Create the record in ``sudo()`` (the test user is, by default, sys admin)
            # and then check what happens when 2 different users (w/ and w/o access to
            # the wizard) try to execute method ``button_open_file_manager()``
            direction = "input" if state.startswith("input") else "output"
            rec = self._create_record(type_code.format(direction), state, content)
            for user in test_users:
                with self.subTest(user=user.login, state=state, content=content):
                    rec = rec.with_user(user)
                    if rec._can_use_file_manager():
                        with RC(self.env["edi.exchange.record.file.manager"], []) as rc:
                            res = rec.button_open_file_manager()
                        self.assertEqual(len(rc.records), 1)
                        wiz = rc.records
                        self.assertIsInstance(res, dict)
                        self.assertEqual(
                            res,
                            {
                                "type": "ir.actions.act_window",
                                "name": wiz._description,
                                "res_model": wiz._name,
                                "res_id": wiz.id,
                                "view_mode": "form",
                                "target": "new",
                                "context": dict(
                                    rec.env.context, dialog_size="extra-large"
                                ),
                            },
                        )
                    else:
                        with self.assertRaisesRegex(
                            UserError, "The file manager cannot be used now"
                        ):
                            rec.button_open_file_manager()
