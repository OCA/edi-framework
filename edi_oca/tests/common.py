# ruff: noqa: F401

from odoo.tests import tagged

from odoo.addons.edi_component_oca.tests.common import (
    EDIBackendCommonComponentRegistryTestCase,
    EDIBackendCommonComponentTestCase,
)
from odoo.addons.edi_core_oca.tests.common import (
    EDIBackendCommonTestCase as EDICoreBackendCommonTestCase,
)
from odoo.addons.edi_core_oca.tests.common import (
    EDIBackendTestMixin,
)


@tagged("post_install", "-at_install")
class EDIBackendCommonTestCase(EDICoreBackendCommonTestCase):
    pass
