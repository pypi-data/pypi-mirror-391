import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        "external_dependencies_override": {
            "python": {
                "otrs_somconnexio": "otrs_somconnexio==0.7.2",
            },
        },
    },
)
