from . import test_record
from . import test_backend_jobs
from . import test_backend_output_jobs


# We want to execute the same tests from the original modules to ensure
# that everything works as expected.
from odoo.addons.edi_core_oca.tests import (
    test_backend_input,
    test_backend_output,
    test_backend_process,
    test_edi_backend_cron,
    test_quick_exec,
)
