
[![Support the OCA](https://odoo-community.org/readme-banner-image)](https://odoo-community.org/get-involved?utm_source=repo-readme)

# edi-framework
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/edi-framework&target_branch=19.0)
[![Pre-commit Status](https://github.com/OCA/edi-framework/actions/workflows/pre-commit.yml/badge.svg?branch=19.0)](https://github.com/OCA/edi-framework/actions/workflows/pre-commit.yml?query=branch%3A19.0)
[![Build Status](https://github.com/OCA/edi-framework/actions/workflows/test.yml/badge.svg?branch=19.0)](https://github.com/OCA/edi-framework/actions/workflows/test.yml?query=branch%3A19.0)
[![codecov](https://codecov.io/gh/OCA/edi-framework/branch/19.0/graph/badge.svg)](https://codecov.io/gh/OCA/edi-framework)
[![Translation Status](https://translation.odoo-community.org/widgets/edi-framework-19-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/edi-framework-19-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

edi-framework

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[edi_component_oca](edi_component_oca/) | 19.0.1.1.0 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> <a href='https://github.com/etobella'><img src='https://github.com/etobella.png' width='32' height='32' style='border-radius:50%;' alt='etobella'/></a> | Allow to use Connector as a source in EDI
[edi_core_oca](edi_core_oca/) | 19.0.1.5.0 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> <a href='https://github.com/etobella'><img src='https://github.com/etobella.png' width='32' height='32' style='border-radius:50%;' alt='etobella'/></a> | Define backends, exchange types, exchange records, basic automation and views for handling EDI exchanges.
[edi_endpoint_oca](edi_endpoint_oca/) | 19.0.1.2.0 |  | Base module allowing configuration of custom endpoints for EDI framework.
[edi_exchange_deduplicate_oca](edi_exchange_deduplicate_oca/) | 19.0.2.0.0 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> <a href='https://github.com/etobella'><img src='https://github.com/etobella.png' width='32' height='32' style='border-radius:50%;' alt='etobella'/></a> | Mark superseded exchange records as obsolete
[edi_notification_oca](edi_notification_oca/) | 19.0.1.0.0 |  | Define notification activities on exchange records.
[edi_product_oca](edi_product_oca/) | 19.0.1.0.0 |  | EDI framework configuration and base logic for products and units of measure
[edi_purchase_oca](edi_purchase_oca/) | 19.0.1.1.0 |  | Define EDI Configuration for Purchase Orders
[edi_queue_oca](edi_queue_oca/) | 19.0.1.4.1 |  | Set Queue Jobs on EDI
[edi_record_metadata_oca](edi_record_metadata_oca/) | 19.0.1.0.2 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Allow to store metadata for related records.
[edi_sale_oca](edi_sale_oca/) | 19.0.1.1.0 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Configuration and special behaviors for EDI on sales.
[edi_storage_oca](edi_storage_oca/) | 19.0.1.0.0 |  | Base module to allow exchanging files via storage backend (eg: SFTP).
[edi_ubl_oca](edi_ubl_oca/) | 19.0.1.0.0 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Define EDI backend type for UBL.
[edi_webservice_oca](edi_webservice_oca/) | 19.0.1.0.0 | <a href='https://github.com/etobella'><img src='https://github.com/etobella.png' width='32' height='32' style='border-radius:50%;' alt='etobella'/></a> <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Defines webservice integration from EDI Exchange records

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
