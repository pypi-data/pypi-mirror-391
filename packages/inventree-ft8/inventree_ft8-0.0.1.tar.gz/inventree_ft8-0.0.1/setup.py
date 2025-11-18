# -*- coding: utf-8 -*-

import setuptools
from inventree_ft8.version import PLUGIN_VERSION


with open('README.md', encoding='utf-8') as f:
    long_description = f.read()


setuptools.setup(
    name="inventree-ft8",
    version=PLUGIN_VERSION,
    author="Jordan Bush",
    author_email="jordan@malmoset.com",
    description="FT8 Client for InvenTree",
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords="inventree ft8 client",
    url="https://danebramage.org/git/",
    license="MIT",
    packages=setuptools.find_packages(),
    setup_requires=[
        "wheel",
        "twine",
    ],
    python_requires=">=3.6",
    entry_points={
        "inventree_plugins": [
            "FT8Client = inventree_ft8.ft8_client:FT8Client"
        ]
    },
    include_package_data=True,
)
