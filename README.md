
[![Support the OCA](https://odoo-community.org/readme-banner-image)](https://odoo-community.org/get-involved?utm_source=repo-readme)

# edi-framework
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/edi-framework&target_branch=18.0)
[![Pre-commit Status](https://github.com/OCA/edi-framework/actions/workflows/pre-commit.yml/badge.svg?branch=18.0)](https://github.com/OCA/edi-framework/actions/workflows/pre-commit.yml?query=branch%3A18.0)
[![Build Status](https://github.com/OCA/edi-framework/actions/workflows/test.yml/badge.svg?branch=18.0)](https://github.com/OCA/edi-framework/actions/workflows/test.yml?query=branch%3A18.0)
[![codecov](https://codecov.io/gh/OCA/edi-framework/branch/18.0/graph/badge.svg)](https://codecov.io/gh/OCA/edi-framework)
[![Translation Status](https://translation.odoo-community.org/widgets/edi-framework-18-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/edi-framework-18-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

edi-framework

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[edi_account_core_oca](edi_account_core_oca/) | 18.0.1.1.1 | <a href='https://github.com/etobella'><img src='https://github.com/etobella.png' width='32' height='32' style='border-radius:50%;' alt='etobella'/></a> | Define EDI Configuration for Account Moves
[edi_account_oca](edi_account_oca/) | 18.0.1.1.1 | <a href='https://github.com/etobella'><img src='https://github.com/etobella.png' width='32' height='32' style='border-radius:50%;' alt='etobella'/></a> | Define some component listeners for Account Moves
[edi_component_oca](edi_component_oca/) | 18.0.1.1.0 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> <a href='https://github.com/etobella'><img src='https://github.com/etobella.png' width='32' height='32' style='border-radius:50%;' alt='etobella'/></a> | Allow to use Connector as a source in EDI
[edi_core_oca](edi_core_oca/) | 18.0.1.7.7 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> <a href='https://github.com/etobella'><img src='https://github.com/etobella.png' width='32' height='32' style='border-radius:50%;' alt='etobella'/></a> | Define backends, exchange types, exchange records, basic automation and views for handling EDI exchanges.
[edi_endpoint_oca](edi_endpoint_oca/) | 18.0.1.0.3 |  | Base module allowing configuration of custom endpoints for EDI framework.
[edi_exchange_deduplicate_oca](edi_exchange_deduplicate_oca/) | 18.0.1.0.0 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> <a href='https://github.com/etobella'><img src='https://github.com/etobella.png' width='32' height='32' style='border-radius:50%;' alt='etobella'/></a> | Introduce a deduplication mechanism at the sending step
[edi_exchange_template_oca](edi_exchange_template_oca/) | 18.0.1.4.0 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Allows definition of exchanges via templates.
[edi_exchange_template_party_data](edi_exchange_template_party_data/) | 18.0.1.1.1 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Glue module between edi_exchange_template and edi_party_data
[edi_notification_oca](edi_notification_oca/) | 18.0.1.0.0 |  | Define notification activities on exchange records.
[edi_oca](edi_oca/) | 18.0.1.5.2 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> <a href='https://github.com/etobella'><img src='https://github.com/etobella.png' width='32' height='32' style='border-radius:50%;' alt='etobella'/></a> | Integrate all EDI modules together
[edi_party_data_oca](edi_party_data_oca/) | 18.0.1.1.1 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Allow to configure and retrieve party information for EDI exchanges.
[edi_party_helper_oca](edi_party_helper_oca/) | 18.0.1.0.1 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Retrieve party information for EDI exchanges, without any component dependency.
[edi_product_oca](edi_product_oca/) | 18.0.1.0.0 |  | EDI framework configuration and base logic for products and products packaging
[edi_purchase_oca](edi_purchase_oca/) | 18.0.1.0.0 |  | Define EDI Configuration for Purchase Orders
[edi_purchase_ubl_output_oca](edi_purchase_ubl_output_oca/) | 18.0.1.0.0 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Handle outbound exchanges for purchases.
[edi_queue_oca](edi_queue_oca/) | 18.0.1.0.2 |  | Set Queue Jobs on EDI
[edi_record_metadata_oca](edi_record_metadata_oca/) | 18.0.1.0.5 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Allow to store metadata for related records.
[edi_sale_endpoint](edi_sale_endpoint/) | 18.0.1.0.0 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Glue module between edi_sale_oca and edi_endpoint_oca.
[edi_sale_input_oca](edi_sale_input_oca/) | 18.0.1.0.2 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Process incoming sale orders with the EDI framework.
[edi_sale_oca](edi_sale_oca/) | 18.0.1.0.1 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Configuration and special behaviors for EDI on sales.
[edi_sale_stock_oca](edi_sale_stock_oca/) | 18.0.1.0.0 | <a href='https://github.com/ivantodorovich'><img src='https://github.com/ivantodorovich.png' width='32' height='32' style='border-radius:50%;' alt='ivantodorovich'/></a> | Configuration and special behaviors for EDI on sales & stock.
[edi_sale_ubl_oca](edi_sale_ubl_oca/) | 18.0.1.0.2 |  | Configuration and special behaviors for EDI UBL exchanges related to sales.
[edi_sale_ubl_output_oca](edi_sale_ubl_output_oca/) | 18.0.1.3.0 |  | Configuration and special behaviors for EDI on sales.
[edi_state_oca](edi_state_oca/) | 18.0.1.0.3 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Allow to assign specific EDI states to related records.
[edi_stock_oca](edi_stock_oca/) | 18.0.1.0.1 |  | Define EDI Configuration for Stock
[edi_storage_oca](edi_storage_oca/) | 18.0.1.1.0 |  | Base module to allow exchanging files via storage backend (eg: SFTP).
[edi_storage_queue_oca](edi_storage_queue_oca/) | 18.0.1.0.0 |  | Integrates EDI Storage with Queue
[edi_ubl_oca](edi_ubl_oca/) | 18.0.1.0.1 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Define EDI backend type for UBL.
[edi_ubl_output_base_oca](edi_ubl_output_base_oca/) | 18.0.1.2.0 |  | Generic UBL party/address qweb templates for the EDI framework.
[edi_webservice_oca](edi_webservice_oca/) | 18.0.1.0.2 | <a href='https://github.com/etobella'><img src='https://github.com/etobella.png' width='32' height='32' style='border-radius:50%;' alt='etobella'/></a> <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Defines webservice integration from EDI Exchange records
[edi_xml_oca](edi_xml_oca/) | 18.0.1.0.2 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Base module for EDI exchange using XML files.

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
