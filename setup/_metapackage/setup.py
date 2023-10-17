import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-edi-framework",
    description="Meta package for oca-edi-framework Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-edi_account_oca>=16.0dev,<16.1dev',
        'odoo-addon-edi_oca>=16.0dev,<16.1dev',
        'odoo-addon-edi_record_metadata_oca>=16.0dev,<16.1dev',
        'odoo-addon-edi_state_oca>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
