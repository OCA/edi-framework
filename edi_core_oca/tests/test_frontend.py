# Copyright 2025 Dixmit
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
import odoo

from odoo.addons.web.tests.test_js import WebSuite


@odoo.tests.tagged("post_install", "-at_install")
class TestEdiCoreOCAFrontend(WebSuite):
    """Test EDI Core OCA Frontend"""

    def get_hoot_filters(self):
        self._test_params = [("+", "@edi_core_oca")]
        return super().get_hoot_filters()

    def test_edi_core_oca(self):
        self.test_unit_desktop()
