# Copyright 2020 Dixmit
# @author: Enric Tobella
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.exceptions import AccessError
from odoo.orm.model_classes import add_to_registry
from odoo.tools import mute_logger

from .common import EDIBackendCommonTestCase


class TestEDIExchangeRecordSecurity(EDIBackendCommonTestCase):
    @classmethod
    def _setup_env(cls):
        # Load fake models ->/
        from .fake_models import EdiExchangeConsumerTest, EdiTestExecution

        add_to_registry(cls.registry, EdiTestExecution)
        add_to_registry(cls.registry, EdiExchangeConsumerTest)
        cls.registry._setup_models__(
            cls.env.cr, ["edi.framework.test.execution", "edi.exchange.consumer.test"]
        )
        cls.registry.init_models(
            cls.env.cr,
            ["edi.framework.test.execution", "edi.exchange.consumer.test"],
            {"models_to_check": True},
        )
        cls.addClassCleanup(cls.registry.__delitem__, "edi.framework.test.execution")
        cls.addClassCleanup(cls.registry.__delitem__, "edi.exchange.consumer.test")
        return super()._setup_env()

    # pylint: disable=W8110
    @classmethod
    def _setup_records(cls):
        super()._setup_records()
        cls.group = cls.env["res.groups"].create({"name": "Demo Group"})
        model = cls.env["ir.model"]._get("edi.exchange.consumer.test")
        cls.ir_access = cls.env["ir.model.access"].create(
            {
                "name": "model access",
                "model_id": model.id,
                "group_id": cls.group.id,
                "perm_read": True,
                "perm_write": True,
                "perm_create": True,
                "perm_unlink": True,
            }
        )
        cls.rule = cls.env["ir.rule"].create(
            {
                "name": "Exchange Record rule demo",
                "model_id": model.id,
                "domain_force": "[('name', '=', 'test')]",
                "groups": [(4, cls.group.id)],
            }
        )
        cls.user = (
            cls.env["res.users"]
            .with_context(no_reset_password=True, mail_notrack=True)
            .create(
                {
                    "name": "Poor Partner (not integrating one)",
                    "email": "poor.partner@ododo.com",
                    "login": "poorpartner",
                    "group_ids": [(6, 0, [cls.env.ref("base_edi.group_edi_user").id])],
                }
            )
        )
        cls.consumer_record = cls.env["edi.exchange.consumer.test"].create(
            {"name": "test"}
        )
        cls.exchange_type_out.exchange_filename_pattern = "{record.id}"

    def create_record(self, user=False):
        vals = {
            "model": self.consumer_record._name,
            "res_id": self.consumer_record.id,
        }
        backend = self.backend
        if user:
            backend = backend.with_user(user)
        return backend.create_record("test_csv_output", vals)

    def test_superuser_create(self):
        exchange_record = self.create_record()
        self.assertTrue(exchange_record)

    def test_group_create(self):
        self.user.write({"group_ids": [(4, self.group.id)]})
        exchange_record = self.create_record()
        self.assertTrue(exchange_record)

    @mute_logger("odoo.addons.base.models.ir_rule")
    def test_rule_no_create(self):
        self.user.write({"group_ids": [(4, self.group.id)]})
        self.consumer_record.name = "no_rule"
        with self.assertRaisesRegex(AccessError, "doesn't have 'write' access to"):
            self.create_record(self.user)

    @mute_logger("odoo.addons.base.models.ir_model")
    def test_no_group_no_create(self):
        with self.assertRaises(AccessError):
            self.create_record(self.user)

    @mute_logger("odoo.addons.base.models.ir_model")
    def test_no_group_no_read(self):
        exchange_record = self.create_record()
        with self.assertRaisesRegex(AccessError, "You are not allowed to access"):
            exchange_record.with_user(self.user).read()

    @mute_logger("odoo.addons.base.models.ir_rule")
    def test_rule_no_read(self):
        exchange_record = self.create_record()
        self.user.write({"group_ids": [(4, self.group.id)]})
        self.assertTrue(exchange_record.with_user(self.user).read())
        self.consumer_record.name = "no_rule"
        with self.assertRaisesRegex(
            AccessError, "Looks like you have stumbled upon some top-secret records"
        ):
            exchange_record.with_user(self.user).read()

    @mute_logger("odoo.addons.base.models.ir_model")
    def test_no_group_no_unlink(self):
        exchange_record = self.create_record()
        with self.assertRaises(AccessError):
            exchange_record.with_user(self.user).unlink()

    @mute_logger("odoo.models.unlink")
    def test_group_unlink(self):
        exchange_record = self.create_record()
        self.user.write({"group_ids": [(4, self.group.id)]})
        self.assertTrue(exchange_record.with_user(self.user).unlink())

    @mute_logger("odoo.addons.base.models.ir_rule")
    def test_rule_no_unlink(self):
        exchange_record = self.create_record()
        self.user.write({"group_ids": [(4, self.group.id)]})
        self.consumer_record.name = "no_rule"
        with self.assertRaisesRegex(AccessError, "doesn't have 'write' access to"):
            exchange_record.with_user(self.user).unlink()

    def test_no_group_no_search(self):
        exchange_record = self.create_record()
        self.assertEqual(
            0,
            self.env["edi.exchange.record"]
            .with_user(self.user)
            .search_count([("id", "=", exchange_record.id)]),
        )

    def test_group_search(self):
        exchange_record = self.create_record()
        self.user.write({"group_ids": [(4, self.group.id)]})
        self.assertEqual(
            1,
            self.env["edi.exchange.record"]
            .with_user(self.user)
            .search_count([("id", "=", exchange_record.id)]),
        )

    def test_rule_no_search(self):
        exchange_record = self.create_record()
        self.user.write({"group_ids": [(4, self.group.id)]})
        self.consumer_record.name = "no_rule"
        self.assertEqual(
            0,
            self.env["edi.exchange.record"]
            .with_user(self.user)
            .search_count([("id", "=", exchange_record.id)]),
        )

    def test_search_no_record(self):
        # Consumer record no longer exists:
        #  exchange_record is hidden in search
        exchange_record = self.create_record()
        exchange_record.res_id = -1
        self.user.write({"group_ids": [(4, self.group.id)]})
        logger_name = "odoo.addons.edi_core_oca.models.edi_exchange_record"
        expected_msg = (
            f"WARNING:{logger_name}:"
            f"Deleted record {exchange_record.model},{exchange_record.res_id} "
            f"is referenced by edi.exchange.record [{exchange_record.id}]"
        )
        with self.assertLogs(logger_name, "WARNING") as watcher:
            self.assertEqual(
                0,
                self.env["edi.exchange.record"]
                .with_user(self.user)
                .search_count([("id", "=", exchange_record.id)]),
            )
            self.assertEqual(watcher.output, [expected_msg])

    def test_search_no_record_admin(self):
        # Consumer record no longer exists:
        #  user with group "Settings" has access
        exchange_record = self.create_record()
        exchange_record.res_id = -1
        admin_group = self.env.ref("base.group_system")
        self.user.write({"group_ids": [(4, self.group.id), (4, admin_group.id)]})
        logger_name = "odoo.addons.edi_core_oca.models.edi_exchange_record"
        with self.assertLogs(logger_name, "WARNING"):
            self.assertEqual(
                1,
                self.env["edi.exchange.record"]
                .with_user(self.user)
                .search_count([("id", "=", exchange_record.id)]),
            )

    @mute_logger("odoo.addons.base.models.ir_model")
    def test_no_group_no_write(self):
        exchange_record = self.create_record()
        with self.assertRaises(AccessError):
            exchange_record.with_user(self.user).write({"external_identifier": "1234"})

    def test_group_write(self):
        exchange_record = self.create_record()
        self.user.write({"group_ids": [(4, self.group.id)]})
        exchange_record.with_user(self.user).write({"external_identifier": "1234"})
        self.assertEqual(exchange_record.external_identifier, "1234")

    @mute_logger("odoo.addons.base.models.ir_rule")
    def test_rule_no_write(self):
        exchange_record = self.create_record()
        self.user.write({"group_ids": [(4, self.group.id)]})
        self.consumer_record.name = "no_rule"
        with self.assertRaisesRegex(AccessError, "doesn't have 'write' access"):
            exchange_record.with_user(self.user).write({"external_identifier": "1234"})

    @mute_logger("odoo.addons.base.models.ir_model")
    def test_no_group_no_read_child(self):
        exchange_record = self.create_record()
        model = self.consumer_record
        # Create child record without specific model and res_id
        # It should follow the access rights of the parent
        child_exchange_record = self.backend.create_record(
            "test_csv_output", {"parent_id": exchange_record.id}
        )
        msg = rf"not allowed to access '{model._description}' \({model._name}\)"
        with self.assertRaisesRegex(AccessError, msg):
            child_exchange_record.with_user(self.user).read()

    def test_search_pagination_with_inaccessible_middle_records(self):
        """
        Regression test:
        If some records in the first page are filtered out due to access rules,
        _search must fetch additional records from next pages without truncating them.
        """

        self.user.write({"group_ids": [(4, self.group.id)]})

        # Two different companies are used to trigger multi-company access filtering
        company_1 = self.env.ref("base.main_company")
        company_2 = self.env["res.company"].create({"name": "Other Company"})

        # Three target records:
        # - consumer_c1 and consumer_c3 belong to the active company and are readable
        # - consumer_c2 belongs to another company and will be filtered out
        # by access rules
        consumer_c1 = self.env["res.partner"].create(
            {"name": "c1-a", "company_id": company_1.id}
        )
        consumer_c2 = self.env["res.partner"].create(
            {"name": "c2", "company_id": company_2.id}
        )
        consumer_c3 = self.env["res.partner"].create(
            {"name": "c1-b", "company_id": company_1.id}
        )

        # One EDI records pointing to readable target records
        self.backend.create_record(
            "test_csv_output",
            {"model": consumer_c1._name, "res_id": consumer_c1.id},
        )

        # One EDI records pointing to records from another company
        self.backend.create_record(
            "test_csv_output",
            {"model": consumer_c2._name, "res_id": consumer_c2.id},
        )

        # One EDI records pointing to readable target records
        visible_id_2 = self.backend.create_record(
            "test_csv_output",
            {"model": consumer_c3._name, "res_id": consumer_c3.id},
        ).id

        # Restrict the environment to company_1 only, activating the multi-company rule
        # that will hide records pointing to consumer_c2
        env_company_1 = self.env(
            context=dict(self.env.context, allowed_company_ids=[company_1.id])
        )

        # Execute the search as a non-superuser:
        # - super()._search returns the first 2 IDs (1 visible + 1 hidden)
        # - custom logic removes the 1 hidden
        # - pagination logic fetches 1 more record from the next page
        records = (
            env_company_1["edi.exchange.record"]
            .with_user(self.user)
            .search([], limit=2, order="id asc")
        )

        # The result must NOT be truncated: the search should still return `
        # limit` records
        self.assertEqual(
            len(records),
            2,
            "Search results were truncated when inaccessible records were "
            "present in the first page",
        )

        # The records fetched from the second page must be present in the final result
        self.assertIn(visible_id_2, records.ids)
