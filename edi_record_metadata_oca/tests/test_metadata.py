# Copyright 2023 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo_test_helper import FakeModelLoader

from odoo import fields

from odoo.addons.edi_core_oca.tests.common import EDIBackendCommonTestCase


class TestEDIMetadata(EDIBackendCommonTestCase):
    def setUp(self):
        super().setUp()
        self.loader = FakeModelLoader(self.env, self.__module__)
        self.loader.backup_registry()
        from .fake_models import EDIMetadataConsumerFake

        self.loader.update_registry((EDIMetadataConsumerFake,))
        self.consumer_model = self.env[EDIMetadataConsumerFake._name]

        self.exc_type = self._create_exchange_type(
            name="Metadata test",
            code="metadata_test",
            direction="output",
        )
        self.exc_record = self.backend.create_record(self.exc_type.code, {})

    def tearDown(self):
        self.loader.restore_registry()
        super().tearDown()

    def test_fields(self):
        self.exc_record.edi_set_metadata({"foo": "baz", "bar": "waa"})
        self.assertTrue(self.exc_record.metadata)
        self.assertTrue(self.exc_record.metadata_display)

    def test_no_store(self):
        consumer_record = self.consumer_model.create(
            {
                "name": "Test Consumer",
                "number": 10.0,
                "origin_exchange_record_id": self.exc_record.id,
            }
        )
        self.assertFalse(consumer_record._edi_get_metadata())
        self.assertFalse(self.exc_record.edi_get_metadata())

    def test_store(self):
        vals = {
            "name": "Test Consumer",
            "number": 10.0,
            "origin_exchange_record_id": self.exc_record.id,
            "a_date": fields.Date.today(),
            "a_datetime": fields.Datetime.now(),
        }
        consumer_record = self.consumer_model.with_context(
            edi_framework_action="generate"
        ).create(vals)
        expected = {
            "name": "Test Consumer",
            "number": 10.0,
            "a_date": fields.Date.to_string(vals["a_date"]),
            "a_datetime": fields.Datetime.to_string(vals["a_datetime"]),
            "origin_exchange_record_id": self.exc_record.id,
            "additional": True,
        }
        self.assertEqual(consumer_record._edi_get_metadata(), expected)
        self.assertEqual(self.exc_record.edi_get_metadata(), expected)
