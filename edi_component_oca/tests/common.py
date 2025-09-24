# Copyright 2020 ACSONE
# Copyright 2020 Dixmit
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo.tests.common import tagged

from odoo.addons.component.tests.common import (
    TransactionComponentCase,
    TransactionComponentRegistryCase,
)
from odoo.addons.edi_core_oca.tests.common import EDIBackendTestMixin


@tagged("-at_install", "post_install")
class EDIBackendCommonComponentTestCase(TransactionComponentCase, EDIBackendTestMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_env()
        cls._setup_records()

    @classmethod
    def _create_exchange_type(cls, **kw):
        model = cls.env.ref("edi_component_oca.model_edi_oca_component_handler")
        kw.setdefault("receive_model_id", model.id)
        kw.setdefault("generate_model_id", model.id)
        kw.setdefault("input_validate_model_id", model.id)
        kw.setdefault("output_validate_model_id", model.id)
        kw.setdefault("send_model_id", model.id)
        kw.setdefault("process_model_id", model.id)
        kw.setdefault("check_model_id", model.id)
        return super()._create_exchange_type(**kw)


@tagged("-at_install", "post_install")
class EDIBackendCommonComponentRegistryTestCase(
    TransactionComponentRegistryCase, EDIBackendTestMixin
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_env()
        cls._setup_records()
        cls._setup_registry(cls)
        cls._load_module_components(cls, "edi_component_oca")

    @classmethod
    def _create_exchange_type(cls, **kw):
        model = cls.env.ref("edi_component_oca.model_edi_oca_component_handler")
        kw.setdefault("receive_model_id", model.id)
        kw.setdefault("generate_model_id", model.id)
        kw.setdefault("input_validate_model_id", model.id)
        kw.setdefault("output_validate_model_id", model.id)
        kw.setdefault("send_model_id", model.id)
        kw.setdefault("process_model_id", model.id)
        kw.setdefault("check_model_id", model.id)
        return super()._create_exchange_type(**kw)
