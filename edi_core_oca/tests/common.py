# Copyright 2020 ACSONE
# Copyright 2020 Dixmit
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import os

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
