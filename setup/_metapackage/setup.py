import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-edi-framework",
    description="Meta package for oca-edi-framework Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-edi_account_oca>=16.0dev,<16.1dev',
        'odoo-addon-edi_backend_partner_oca>=16.0dev,<16.1dev',
        'odoo-addon-edi_edifact_oca>=16.0dev,<16.1dev',
        'odoo-addon-edi_endpoint_oca>=16.0dev,<16.1dev',
        'odoo-addon-edi_exchange_deduplicate_oca>=16.0dev,<16.1dev',
        'odoo-addon-edi_exchange_template_oca>=16.0dev,<16.1dev',
        'odoo-addon-edi_notification_oca>=16.0dev,<16.1dev',
        'odoo-addon-edi_oca>=16.0dev,<16.1dev',
        'odoo-addon-edi_partner_oca>=16.0dev,<16.1dev',
        'odoo-addon-edi_party_data_oca>=16.0dev,<16.1dev',
        'odoo-addon-edi_product_multi_barcode_oca>=16.0dev,<16.1dev',
        'odoo-addon-edi_product_oca>=16.0dev,<16.1dev',
        'odoo-addon-edi_record_metadata_oca>=16.0dev,<16.1dev',
        'odoo-addon-edi_sale_edifact_oca>=16.0dev,<16.1dev',
        'odoo-addon-edi_sale_oca>=16.0dev,<16.1dev',
        'odoo-addon-edi_state_oca>=16.0dev,<16.1dev',
        'odoo-addon-edi_stock_oca>=16.0dev,<16.1dev',
        'odoo-addon-edi_storage_oca>=16.0dev,<16.1dev',
        'odoo-addon-edi_ubl_oca>=16.0dev,<16.1dev',
        'odoo-addon-edi_utm_oca>=16.0dev,<16.1dev',
        'odoo-addon-edi_webservice_oca>=16.0dev,<16.1dev',
        'odoo-addon-edi_xml_oca>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
