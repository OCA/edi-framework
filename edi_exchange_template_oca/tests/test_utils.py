# Copyright 2022 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.tests.common import TransactionCase


class TestUtils(TransactionCase):
    def test_firstof(self):
        first_of = self.env["edi.exchange.template.mixin"]._time_utils()["first_of"]
        self.assertEqual(first_of([1, 2, 3]), 1)
        self.assertEqual(first_of([1]), 1)
        self.assertEqual(first_of(1), 1)
        self.assertEqual(first_of([]), None)
        self.assertEqual(first_of(None), None)
        partner_01 = self.env["res.partner"].create({"name": "TEST PARTNER 01"})
        partner_02 = self.env["res.partner"].create({"name": "TEST PARTNER 01"})
        self.assertEqual(first_of(partner_01 | partner_02), partner_01)
        self.assertEqual(first_of(partner_02), partner_02)
