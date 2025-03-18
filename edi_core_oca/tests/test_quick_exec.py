# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from unittest import mock

from .common import EDIBackendCommonTestCase

LOGGERS = ("odoo.addons.edi_core_oca.models.edi_backend", "odoo.addons.queue_job.delay")


class EDIQuickExecTestCase(EDIBackendCommonTestCase):
    def test_quick_exec_on_create_no_call(self):
        vals = {
            "model": self.partner._name,
            "res_id": self.partner.id,
        }
        model = self.env["edi.exchange.record"]
        # quick exec is off, we should not get any call
        with mock.patch.object(type(model), "_execute_next_action") as mocked:
            record0 = self.backend.create_record("test_csv_output", vals)
            mocked.assert_not_called()
            self.assertEqual(record0.edi_exchange_state, "new")
        # enabled but bypassed
        self.exchange_type_out.exchange_file_auto_generate = True
        self.exchange_type_out.quick_exec = True
        with mock.patch.object(type(model), "_execute_next_action") as mocked:
            record0 = self.backend.with_context(
                edi__skip_quick_exec=True
            ).create_record("test_csv_output", vals)
            # quick exec is off, we should not get any call
            mocked.assert_not_called()
            self.assertEqual(record0.edi_exchange_state, "new")
