# Copyright 2020 ACSONE
# Copyright 2021 Camptocamp
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo.orm.model_classes import add_to_registry
from odoo.tests import tagged

from odoo.addons.edi_core_oca.tests.common import EDIBackendCommonTestCase
from odoo.addons.queue_job.tests.common import trap_jobs


@tagged("-at_install", "post_install")
class EDIBackendTestOutputJobsCase(EDIBackendCommonTestCase):
    @classmethod
    def _setup_records(cls):  # pylint:disable=missing-return
        super()._setup_records()
        from odoo.addons.edi_core_oca.tests.fake_models import EdiTestExecution

        add_to_registry(cls.registry, EdiTestExecution)
        cls.registry._setup_models__(cls.env.cr, ["edi.framework.test.execution"])
        cls.registry.init_models(
            cls.env.cr, ["edi.framework.test.execution"], {"models_to_check": True}
        )
        cls.addClassCleanup(cls.registry.__delitem__, "edi.framework.test.execution")
        model = cls.env["ir.model"]._get("edi.framework.test.execution")
        cls.exchange_type_out.generate_model_id = model
        cls.exchange_type_out.send_model_id = model

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        vals = {
            "model": cls.partner._name,
            "res_id": cls.partner.id,
        }
        cls.record = cls.backend.create_record("test_csv_output", vals)
        cls.record.type_id.exchange_file_auto_generate = True

    @classmethod
    def _setup_context(cls):
        # Re-enable jobs
        return dict(super()._setup_context(), queue_job__no_delay=False)

    def test_job(self):
        with trap_jobs() as trap:
            self.backend._check_output_exchange_sync(record_ids=self.record.ids)
            trap.assert_jobs_count(2)
            trap.assert_enqueued_job(
                self.record.action_exchange_generate,
            )
            trap.assert_enqueued_job(
                self.record.action_exchange_send,
            )
            # No matter how many times we schedule jobs
            self.record.action_exchange_generate()
            self.record.action_exchange_generate()
            self.record.action_exchange_generate()
            # identity key should prevent having new jobs for same record same file
            trap.assert_jobs_count(2)
            # but if we change the content
            self.record._set_file_content("something different")
            # 1st call will schedule another job
            self.record.action_exchange_generate()
            # the 2nd one not
            self.record.action_exchange_generate()
            trap.assert_jobs_count(3)
            job = self.record.action_exchange_send()
            self.assertEqual(0, job.priority)
            trap.assert_jobs_count(4)
        # TODO: test input in the same way
