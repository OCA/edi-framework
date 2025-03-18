# Copyright 2020 Creu Blanca
# @author: Enric Tobella
# Copyright 2020 Camptocamp SA
# @author: Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import os
import unittest

from odoo_test_helper import FakeModelLoader

from odoo import Command, fields
from odoo.tests import tagged

from odoo.addons.edi_core_oca.tests.common import EDIBackendCommonTestCase


# This clashes w/ some setup (eg: run tests w/ pytest when edi_storage is installed)
# If you still want to run `edi` tests w/ pytest when this happens, set this env var.
@unittest.skipIf(os.getenv("SKIP_EDI_CONSUMER_CASE"), "Consumer test case disabled.")
@tagged("at_install", "-post_install")
class TestConsumerMixinCase(EDIBackendCommonTestCase):
    @classmethod
    def _setup_env(cls):
        super()._setup_env()
        # Load fake models ->/
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from odoo.addons.edi_core_oca.tests.fake_models import EdiExchangeConsumerTest

        cls.loader.update_registry((EdiExchangeConsumerTest,))
        return super()._setup_env()

    # pylint: disable=W8110
    @classmethod
    def _setup_records(cls):
        super()._setup_records()
        cls.consumer_record = cls.env["edi.exchange.consumer.test"].create(
            {"name": "Test Consumer"}
        )
        cls.exchange_type_out.exchange_filename_pattern = "{record.id}"
        rule_vals = {
            "name": "Test",
            "model_id": cls.env["ir.model"]._get_id(cls.consumer_record._name),
            "kind": "custom",
            "enable_domain": "[]",
            "enable_snippet": """
result = not record._has_exchange_record(exchange_type, exchange_type.backend_id)
""",
        }
        cls.exchange_type_out.write({"rule_ids": [Command.create(rule_vals)]})

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def test_expected_configuration(self):
        # no btn enabled

        def make_config_data(**kw):
            data = {
                "form": {},
                "type": {
                    "id": self.exchange_type_out.id,
                    "name": self.exchange_type_out.name,
                },
            }
            data.update(kw)
            return data

        rule = fields.first(self.exchange_type_out.rule_ids)
        self.assertFalse(self.consumer_record.edi_has_form_config)
        self.assertEqual(
            self.consumer_record.edi_config[str(rule.id)],
            make_config_data(),
        )
        # enable it
        self.exchange_type_out.rule_ids[0].kind = "form_btn"
        self.consumer_record.invalidate_model(["edi_has_form_config", "edi_config"])
        self.assertEqual(
            self.consumer_record.edi_config[str(rule.id)],
            make_config_data(
                form={"btn": {"label": self.exchange_type_out.name, "tooltip": False}}
            ),
        )
        action = self.consumer_record.edi_create_exchange_record(
            self.exchange_type_out.id
        )
        self.assertEqual(action["res_model"], "edi.exchange.record")
        self.consumer_record.invalidate_model()
        self.assertNotIn(
            str(rule.id),
            self.consumer_record.edi_config,
        )
        self.assertTrue(self.consumer_record.exchange_record_ids)
        self.assertEqual(
            self.consumer_record.exchange_record_ids.type_id, self.exchange_type_out
        )
