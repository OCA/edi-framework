# Copyright 2026 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import unittest

from odoo.addons.edi_core_oca.utils import EdiExchangeReturn


class TestEdiExchangeReturn(unittest.TestCase):
    def test_str_without_code(self):
        value = EdiExchangeReturn("Exchange sent")
        self.assertEqual(str(value), "Exchange sent")

    def test_str_with_code(self):
        value = EdiExchangeReturn("Exchange sent", code=200)
        self.assertEqual(str(value), "[200] Exchange sent")

    def test_repr(self):
        value = EdiExchangeReturn("before/after", code=422)
        self.assertEqual(
            repr(value),
            "EdiExchangeReturn(code=422, message='before/after')",
        )
