# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo.addons.edi_core_oca.tests.common import EDIBackendCommonTestCase


class EDIBackendTestCaseBase(EDIBackendCommonTestCase):
    def test_get_component_usage(self):
        vals = {
            "model": self.partner._name,
            "res_id": self.partner.id,
        }
        record = self.backend.create_record("test_csv_input", vals)
        candidates = self.backend._get_component_usage_candidates(record, "process")
        self.assertEqual(
            candidates,
            ["input.process"],
        )
        record = self.backend.create_record("test_csv_output", vals)
        candidates = self.backend._get_component_usage_candidates(record, "generate")
        self.assertEqual(
            candidates,
            ["output.generate"],
        )
        # set advanced settings on type
        settings = """
        components:
            generate:
                usage: my.special.generate
            send:
                usage: my.special.send
        """
        record.type_id.advanced_settings_edit = settings
        candidates = self.backend._get_component_usage_candidates(record, "generate")
        self.assertEqual(
            candidates,
            ["my.special.generate", "output.generate"],
        )
        candidates = self.backend._get_component_usage_candidates(record, "send")
        self.assertEqual(
            candidates,
            ["my.special.send", "output.send"],
        )
