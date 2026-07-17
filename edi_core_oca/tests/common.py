# Copyright 2020 ACSONE
# Copyright 2020 Dixmit
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import os

from odoo.orm.model_classes import add_to_registry
from odoo.tests.common import TransactionCase


class EDIBackendTestMixin:
    @classmethod
    def _setup_context(cls, **kw):
        return dict(
            cls.env.context, tracking_disable=True, queue_job__no_delay=True, **kw
        )

    @classmethod
    def _setup_env(cls, ctx=None):
        ctx = ctx or {}
        cls.env = cls.env(context=cls._setup_context(**ctx))
        # Register EdiTestExecution early so _create_exchange_type can set default
        # handler models — the new @api.constrains on edi.exchange.type requires
        # send_model_id (output) and process_model_id (input) to be set.
        # Guard prevents double-registration when individual test classes also call
        # add_to_registry; pop() in cleanup is safe even if __delitem__ already ran.
        if "edi.framework.test.execution" not in cls.registry:
            from .fake_models import EdiTestExecution

            add_to_registry(cls.registry, EdiTestExecution)
            cls.registry._setup_models__(cls.env.cr, ["edi.framework.test.execution"])
            cls.registry.init_models(
                cls.env.cr, ["edi.framework.test.execution"], {"models_to_check": True}
            )
            cls.addClassCleanup(
                lambda: cls.registry.__delitem__("edi.framework.test.execution")
                if "edi.framework.test.execution" in cls.registry
                else None
            )

    @classmethod
    def _setup_records(cls):
        cls.backend = cls._get_backend()
        cls.backend_type_code = cls.backend.backend_type_id.code
        cls.backend_model = cls.env["edi.backend"]
        cls.backend_type_model = cls.env["edi.backend.type"]
        cls.exchange_type_in = cls._create_exchange_type(
            name="Test CSV input",
            code="test_csv_input",
            direction="input",
            exchange_file_ext="csv",
            exchange_filename_pattern="{record.ref}-{type.code}-{dt}",
        )
        cls.exchange_type_out = cls._create_exchange_type(
            name="Test CSV output",
            code="test_csv_output",
            direction="output",
            exchange_file_ext="csv",
            exchange_filename_pattern="{record.ref}-{type.code}-{dt}",
        )
        cls.exchange_type_out_ack = cls._create_exchange_type(
            name="Test CSV output ACK",
            code="test_csv_output_ack",
            direction="output",
            exchange_file_ext="txt",
            exchange_filename_pattern="{record.ref}-{type.code}-{dt}",
        )
        cls.exchange_type_out.ack_type_id = cls.exchange_type_out_ack
        cls.partner = cls.env["res.partner"].create({"name": "EDI EXC TEST"})
        cls.partner.ref = "EDI_EXC_TEST"
        cls.sequence = cls.env["ir.sequence"].create(
            {
                "code": "test_sequence",
                "name": "Test sequence",
                "implementation": "no_gap",
                "padding": 7,
            }
        )

    def read_test_file(self, filename):
        path = os.path.join(os.path.dirname(__file__), "examples", filename)
        with open(path) as thefile:
            return thefile.read()

    @classmethod
    def _get_backend_type(cls):
        return cls.env["edi.backend.type"].create(
            {
                "name": "Demo backend type",
                "code": "demo_backend",
            }
        )

    @classmethod
    def _get_backend(cls):
        return cls.env["edi.backend"].create(
            {
                "name": "Demo backend",
                "backend_type_id": cls._get_backend_type().id,
            }
        )

    @classmethod
    def _create_exchange_type(cls, **kw):
        # Mirror the pattern in edi_component_oca/tests/common.py: provide default
        # handler models so every test exchange type satisfies the new constraint.
        # Callers can override individual fields by passing explicit values.
        # When the fake execution model is not registered (test classes that
        # skip _setup_env), fall back to the no-op handler shipped by the
        # module so the constraint is still satisfied.
        handler_model_name = (
            "edi.framework.test.execution"
            if "edi.framework.test.execution" in cls.registry
            else "edi.oca.handler.noop"
        )
        handler_model = cls.env["ir.model"]._get(handler_model_name)
        if handler_model:
            kw.setdefault("receive_model_id", handler_model.id)
            kw.setdefault("generate_model_id", handler_model.id)
            kw.setdefault("input_validate_model_id", handler_model.id)
            kw.setdefault("output_validate_model_id", handler_model.id)
            kw.setdefault("send_model_id", handler_model.id)
            kw.setdefault("process_model_id", handler_model.id)
            kw.setdefault("check_model_id", handler_model.id)
        model = cls.env["edi.exchange.type"]
        vals = {
            "name": "Test CSV exchange",
            "backend_id": cls.backend.id,
            "backend_type_id": cls.backend.backend_type_id.id,
        }
        vals.update(kw)
        return model.create(vals)


class EDIBackendCommonTestCase(TransactionCase, EDIBackendTestMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_env()
        cls._setup_records()

    def _make_global_error_conf(self, exchange_type):
        """Register a global ``edi.configuration`` bound to the
        ``on_edi_exchange_error`` event.

        Its snippet writes a marker on the configuration so a test can assert
        the error event actually fired. This is the observable behaviour that
        distinguishes an errored exchange (which must notify, e.g. create the
        activities handled by ``edi_notification_oca``) from one that merely
        posts a chatter message via ``notify_action_complete``.
        """
        trigger = self.env.ref("edi_core_oca.edi_config_trigger_record_error")
        return self.env["edi.configuration"].create(
            {
                "name": "Test notify on error",
                "active": True,
                "backend_id": self.backend.id,
                "type_id": exchange_type.id,
                "trigger_id": trigger.id,
                "is_global": True,
                "snippet_do": "conf.write({'description': 'error-event-fired'})",
            }
        )
