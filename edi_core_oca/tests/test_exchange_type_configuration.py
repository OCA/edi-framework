# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.orm.model_classes import add_to_registry

from .common import EDIBackendCommonTestCase


class EDIBackendTestOutputCase(EDIBackendCommonTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        vals = {
            "model": cls.partner._name,
            "res_id": cls.partner.id,
        }
        cls.record = cls.backend.create_record("test_csv_output", vals)

    @classmethod
    def _setup_records(cls):  # pylint:disable=missing-return
        super()._setup_records()
        # Load fake models ->/
        from .fake_models import EdiTestExecution, EdiTestExecutionExtra

        add_to_registry(cls.registry, EdiTestExecution)
        cls.registry._setup_models__(cls.env.cr, ["edi.framework.test.execution"])
        cls.registry.init_models(
            cls.env.cr, ["edi.framework.test.execution"], {"models_to_check": True}
        )
        add_to_registry(cls.registry, EdiTestExecutionExtra)
        cls.registry._setup_models__(cls.env.cr, ["edi.framework.test.execution.extra"])
        cls.registry.init_models(
            cls.env.cr,
            ["edi.framework.test.execution.extra"],
            {"models_to_check": True},
        )
        cls.addClassCleanup(cls.registry.__delitem__, "edi.framework.test.execution")
        cls.addClassCleanup(
            cls.registry.__delitem__, "edi.framework.test.execution.extra"
        )
        cls.ExecutionAbstractModel = cls.env["edi.framework.test.execution"]
        cls.ExecutionAbstractModelExtra = cls.env["edi.framework.test.execution.extra"]
        cls.model = cls.env["ir.model"]._get("edi.framework.test.execution")
        cls.exchange_type_out.generate_model_id = cls.model
        cls.exchange_type_out.send_model_id = cls.model

    def setUp(self):
        super().setUp()
        self.ExecutionAbstractModel.reset_faked("generate")
        self.ExecutionAbstractModelExtra.reset_faked("validate")

    def test_multiple_configuration(self):
        vals = {
            "model": self.partner._name,
            "res_id": self.partner.id,
        }
        record = self.backend.create_record("test_csv_output", vals)
        record.type_id.generate_model_id = self.env["ir.model"].search(
            [("model", "=", "edi.framework.test.execution.extra")]
        )
        record.action_exchange_generate()
        self.assertFalse(
            self.ExecutionAbstractModel.check_called_for(record, "generate")
        )
        self.assertTrue(
            self.ExecutionAbstractModelExtra.check_called_for(record, "generate")
        )
