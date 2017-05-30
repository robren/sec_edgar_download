#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'bs4', 
    'docopt>=0.6.0',
    'lxml', 
    'pandas',
    'requests'
]

test_requirements = [
        'pytest'
]

setup(
    name='sec_edgar_download',
    version='0.1.1',
    description="Downloads sec xbrl filings",
    long_description=readme + '\n\n' + history,
    author="Robert Rennison",
    author_email='rob@robren.net',
    url='https://github.com/robren/sec_edgar_download',
    packages=[
        'sec_edgar_download',
    ],
    package_dir={'sec_edgar_download':
                 'sec_edgar_download'},
    entry_points={
        'console_scripts': [
            'sec_edgar_download=sec_edgar_download.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='sec_edgar_download',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
