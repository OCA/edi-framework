# Copyright 2026 Camptocamp SA
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.orm.model_classes import add_to_registry
from odoo.tests.common import TransactionCase


class PayloadTrackingTestCase(TransactionCase):
    """Register the test consumer model and create two of its records."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_fake_models()
        cls.consumer_model = cls.env["edi.payload.consumer.test"]
        cls.payload_model = cls.env["edi.payload.output"]
        cls.record = cls.consumer_model.create({"name": "Record 1"})
        cls.other_record = cls.consumer_model.create({"name": "Record 2"})

    @classmethod
    def _setup_fake_models(cls):
        """Add the test consumer model to the registry, removed on cleanup."""
        from .fake_models import EDIPayloadConsumerTest

        model_name = EDIPayloadConsumerTest._name
        add_to_registry(cls.registry, EDIPayloadConsumerTest)
        cls.registry._setup_models__(cls.env.cr, [model_name])
        cls.registry.init_models(cls.env.cr, [model_name], {"models_to_check": True})
        cls.addClassCleanup(cls.registry.__delitem__, model_name)
