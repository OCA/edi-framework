
[![Support the OCA](https://odoo-community.org/readme-banner-image)](https://odoo-community.org/get-involved?utm_source=repo-readme)

# edi-framework
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/edi-framework&target_branch=16.0)
[![Pre-commit Status](https://github.com/OCA/edi-framework/actions/workflows/pre-commit.yml/badge.svg?branch=16.0)](https://github.com/OCA/edi-framework/actions/workflows/pre-commit.yml?query=branch%3A16.0)
[![Build Status](https://github.com/OCA/edi-framework/actions/workflows/test.yml/badge.svg?branch=16.0)](https://github.com/OCA/edi-framework/actions/workflows/test.yml?query=branch%3A16.0)
[![codecov](https://codecov.io/gh/OCA/edi-framework/branch/16.0/graph/badge.svg)](https://codecov.io/gh/OCA/edi-framework)
[![Translation Status](https://translation.odoo-community.org/widgets/edi-framework-16-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/edi-framework-16-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

{'TODO': 'add repo description.'}

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[edi_account_oca](edi_account_oca/) | 16.0.1.1.0 | <a href='https://github.com/etobella'><img src='https://github.com/etobella.png' width='32' height='32' style='border-radius:50%;' alt='etobella'/></a> | Define EDI Configuration for Account Moves
[edi_backend_partner_oca](edi_backend_partner_oca/) | 16.0.1.0.1 | <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | Add the a partner field to EDI backend
[edi_edifact_oca](edi_edifact_oca/) | 16.0.1.0.0 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Define EDI backend type for EDIFACT.
[edi_endpoint_oca](edi_endpoint_oca/) | 16.0.1.1.1 |  | Base module allowing configuration of custom endpoints for EDI framework.
[edi_exchange_deduplicate_oca](edi_exchange_deduplicate_oca/) | 16.0.1.1.0 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> <a href='https://github.com/etobella'><img src='https://github.com/etobella.png' width='32' height='32' style='border-radius:50%;' alt='etobella'/></a> | Introduce a deduplication mechanism at the sending step
[edi_exchange_template_oca](edi_exchange_template_oca/) | 16.0.1.1.2 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Allows definition of exchanges via templates.
[edi_mrp_oca](edi_mrp_oca/) | 16.0.1.0.0 |  | EDI framework configuration and base logic for manufacturing orders
[edi_notification_oca](edi_notification_oca/) | 16.0.1.0.0 |  | Define notification activities on exchange records.
[edi_oca](edi_oca/) | 16.0.1.16.0 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> <a href='https://github.com/etobella'><img src='https://github.com/etobella.png' width='32' height='32' style='border-radius:50%;' alt='etobella'/></a> | Define backends, exchange types, exchange records, basic automation and views for handling EDI exchanges.
[edi_partner_oca](edi_partner_oca/) | 16.0.1.0.1 |  | EDI framework configuration and base logic for partners
[edi_party_data_oca](edi_party_data_oca/) | 16.0.1.0.0 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Allow to configure and retrieve party information for EDI exchanges.
[edi_product_multi_barcode_oca](edi_product_multi_barcode_oca/) | 16.0.1.0.0 |  | EDI framework configuration and base logic for product barcodes.
[edi_product_oca](edi_product_oca/) | 16.0.1.1.1 |  | EDI framework configuration and base logic for products and products packaging
[edi_record_metadata_oca](edi_record_metadata_oca/) | 16.0.1.0.0 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Allow to store metadata for related records.
[edi_sale_edifact_oca](edi_sale_edifact_oca/) | 16.0.1.1.0 |  | Provide a demo exchange type setting and common tests for EDIFACT standard in EDI on sales.
[edi_sale_oca](edi_sale_oca/) | 16.0.1.2.0 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Configuration and special behaviors for EDI on sales.
[edi_state_oca](edi_state_oca/) | 16.0.1.1.0 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Allow to assign specific EDI states to related records.
[edi_stock_oca](edi_stock_oca/) | 16.0.1.1.2 |  | Define EDI Configuration for Stock
[edi_storage_oca](edi_storage_oca/) | 16.0.1.2.3 |  | Base module to allow exchanging files via storage backend (eg: SFTP).
[edi_ubl_oca](edi_ubl_oca/) | 16.0.1.0.0 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Define EDI backend type for UBL.
[edi_utm_oca](edi_utm_oca/) | 16.0.1.0.0 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Automatically assigns the EDI source to records created through the EDI mechanism.
[edi_webservice_oca](edi_webservice_oca/) | 16.0.1.0.1 | <a href='https://github.com/etobella'><img src='https://github.com/etobella.png' width='32' height='32' style='border-radius:50%;' alt='etobella'/></a> <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Defines webservice integration from EDI Exchange records
[edi_xml_oca](edi_xml_oca/) | 16.0.1.1.2 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Base module for EDI exchange using XML files.

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Odoo Community Association (OCA)
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
