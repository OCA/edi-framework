import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-edi-framework",
    description="Meta package for oca-edi-framework Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-edi_state_oca',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
