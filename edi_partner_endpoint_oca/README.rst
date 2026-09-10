=========================
EDI Partner Endpoint Glue
=========================

This module is a glue addon between ``edi_partner_oca`` and ``edi_endpoint_oca``.

Why it exists
=============

It was created to fix the registry initialization error:

::

    KeyError: 'Field edi_endpoint_id referenced in related field definition
    res.partner.origin_edi_endpoint_id does not exist.'

By depending on both modules and using ``auto_install = True``, Odoo installs
this glue module only when both prerequisites are present, ensuring a safe
module loading order.
