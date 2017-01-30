===============================
sec_edgar_download
===============================


.. image:: https://img.shields.io/pypi/v/sec_edgar_download.svg
        :target: https://pypi.python.org/pypi/sec_edgar_download

.. image:: https://img.shields.io/travis/robren/sec_edgar_download.svg
        :target: https://travis-ci.org/robren/sec_edgar_download

.. image:: https://readthedocs.org/projects/sec-edgar-download/badge/?version=latest
        :target: https://sec-edgar-download.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/robren/sec_edgar_download/shield.svg
     :target: https://pyup.io/repos/github/robren/sec_edgar_download/
     :alt: Updates

A small python library which downloads companies 10-K and 10-Q filings from
the SEC's Edgar website. The Edgar site maintains monthly RSS feeds describing
each of the filings. A cli tool called sec_edgar_download supports downloading
and indexing, in a local sqlite3 database,  the RSS files; as well as
downloading specific 10-K and 10-Q filings. 


sec_edgar_download package
==========================

Submodules
----------

sec_edgar_download.cli module::

    """sec_edgar_dowload

    Usage:
    sec_edgar_download getrss <from-year> <to-year> [--fm <from-month>]
                                            [--tm <to-month] [--wd <dir>]
    sec_edgar_download getxbrl <from-year> <to-year> (-c  <cik> | -t <ticker>)
                                            [--ft <form-type>]  [--wd <dir>]

    sec_edgar_download.py (-h | --help)
    sec_edgar_download.py --version

    Options:
    -h --help             Show this screen.
    -c --cik <cik>        Central Index Key (CIK)
    -t --ticker <ticker>  Ticker symbol
    --version             Show version.
    --fm <from-month>     From month: digits 1 to 12
    --tm <to-month>       To  monthd: digits 1 to 12
    --ft <form-type>      10-K or 10-Q
    --wd <dir>            Working-directory  [default : ./edgar]

    """


* Free software: Apache Software License 2.0
* Documentation: https://sec-edgar-download.readthedocs.io.


Features
--------

- Downloads monthly RSS feeds from the SEC Edgar website.
- Stores the location of the relevant filing along with a companies CIK in an
  sqlite database.
- Downloads 10-Q and 10-K filings for a company over a  specified date range.

Credits
---------

This package was created with Cookiecutter_ and the `robren/cookiecutter-pypackage` a fork of
the `audreyr/cookiecutter-pypackage`_ project template.

.. _`robren/cookiecutter-pypackage`: https://github.com/robren/cookiecutter-pypackage
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

