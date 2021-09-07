#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import os
from os.path import join

from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.md') as history_file:
    history = history_file.read()

# Installed by pip install common-utils-py
# or pip install -e .
install_requirements = [
    'requests==2.21.0',
    'eciespy==0.3.5',
    'eth-keys==0.3.3',
    'rsa==4.7',
    # secp256k1 support was added recently and the latest release does not included it yet
    # so for now we are going to used a fork
    'nevermined-authlib==0.1.0'
]

# Required to run setup.py:
setup_requirements = ['pytest-runner', ]

test_requirements = [
    'contracts-lib-py==0.7.11',
    'web3==5.13.0',
    'coverage',
    'docker',
    'mccabe',
    'pylint',
    'pytest',
    'pytest-watch',
]

# Possibly required by developers of common-utils-py:
dev_requirements = [
    'bumpversion',
    'pkginfo',
    'twine',
    'watchdog',
]

docs_requirements = [
    'Sphinx',
    'sphinxcontrib-apidoc',
]

packages = []
for d, _, _ in os.walk('common_utils_py'):
    if os.path.exists(join(d, '__init__.py')):
        packages.append(d.replace(os.path.sep, '.'))

setup(
    author="nevermined-io",
    author_email='root@nevermined.io',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
    ],
    description="🐳 Library including all the common functionalities used in Python projects",
    extras_require={
        'test': test_requirements,
        'dev': dev_requirements + test_requirements + docs_requirements,
        'docs': docs_requirements,
    },
    install_requires=install_requirements,
    license="Apache Software License 2.0",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords='common-utils-py',
    name='common-utils-py',
    packages=packages,
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/nevermined-io/common-utils-py',
    version='0.7.4',
    zip_safe=False,
)
