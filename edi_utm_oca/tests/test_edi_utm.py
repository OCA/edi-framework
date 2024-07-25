# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo_test_helper import FakeModelLoader

from odoo.addons.edi_oca.tests.common import EDIBackendCommonTestCase


class TestEDIUtm(EDIBackendCommonTestCase):
    @classmethod
    def _setup_records(cls):  # pylint: disable=missing-return
        super()._setup_records()
        cls.exchange_type_in.exchange_filename_pattern = "{record.id}-{type.code}-{dt}"

        # Load fake models ->/
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .fake_models import EDIUtmConsumerFake

        cls.loader.update_registry((EDIUtmConsumerFake,))
        cls.consumer_model = cls.env[EDIUtmConsumerFake._name]

        cls.exc_record_in = cls.backend.create_record(
            cls.exchange_type_in.code, {"edi_exchange_state": "input_received"}
        )

    def test_edi_update_source(self):
        consumer_record = self.consumer_model.create(
            {
                "name": "State Test Consumer",
                "origin_exchange_record_id": self.exc_record_in.id,
            }
        )

        self.assertEqual(
            consumer_record.edi_source_id,
            self.env.ref("edi_utm_oca.utm_source_edi"),
        )

    def test_edi_no_update_source(self):
        self.exchange_type_in.edi_source_id = False
        consumer_record = self.consumer_model.create(
            {
                "name": "State Test Consumer",
                "origin_exchange_record_id": self.exc_record_in.id,
            }
        )

        self.assertFalse(consumer_record.edi_source_id)
