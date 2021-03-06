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

A small python library which downloads companies 10-K and 10-Q  xbrl format filings from
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
    sec_edgar_download getxbrl <from-year> <to-year> (-c  <cik> | -t <ticker> | -f <file>)
                                            [--ft <form-type>]  [--wd <dir>]

    sec_edgar_download.py (-h | --help)
    sec_edgar_download.py --version

    Options:
    -h --help             Show this screen.
    -c --cik <cik>        Central Index Key (CIK)
    -t --ticker <ticker>  Ticker symbol
    -f --file <file>      File containing tickers
    --version             Show version.
    --fm <from-month>     From month: digits 1 to 12
    --tm <to-month>       To month: digits 1 to 12
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
- Downloads 10-Q and 10-K  xbrl filings for a company over a  specified date range.

Usage Examples
--------------

From the command line.

- Firstly download the rss feeds, these get added to a local database
- Next specify which tickers to download the xbrl filings for.

.. code:: bash

	pip install sec_edgar_download
	# Download the rss feeds
	sec_edgar_download getrss 2017 2017
	# Download the xbrl encoded filings
	sec_edgar_download getxbrl 2017 2017 -t AAPL
	
	tree
	.
	└── edgar
		├── edgar.db
		├── filings
		│   ├── aapl-20161231.xml
		│   ├── aapl-20170401.xml
		│   └── aapl-20170701.xml
		└── rss-archives
			├── xbrlrss-2017-01.xml
			├── xbrlrss-2017-02.xml
			├── xbrlrss-2017-03.xml
			├── xbrlrss-2017-04.xml
			├── xbrlrss-2017-05.xml
			├── xbrlrss-2017-06.xml
			├── xbrlrss-2017-07.xml
			├── xbrlrss-2017-08.xml
			├── xbrlrss-2017-09.xml
			├── xbrlrss-2017-10.xml
			├── xbrlrss-2017-11.xml
			└── xbrlrss-2017-12.xml

From within a python script

.. code:: bash

    # Run the following from ipython or Jupyter Notebook

    from sec_edgar_download import indexer as ix
    work_dir = './edgar'
    from_year = 2016
    to_year = 2016
    indexer = ix.SecIndexer(work_dir)
    indexer.download_sec_feeds(from_year, to_year)

    INFO:root:Downloaded RSS feed: ./edgar/rss-archives/xbrlrss-2016-01.xml
    INFO:root:Parsing RSS feed ./edgar/rss-archives/xbrlrss-2016-01.xml
    INFO:root:Downloaded RSS feed: ./edgar/rss-archives/xbrlrss-2016-02.xml
    INFO:root:Parsing RSS feed ./edgar/rss-archives/xbrlrss-2016-02.xml
    INFO:root:Downloaded RSS feed: ./edgar/rss-archives/xbrlrss-2016-03.xml

    ... snip

    INFO:root:Dropped 436 duplicates
    INFO:root:32662 items parsed
    INFO:root:Saved feed details to ./edgar/edgar.db

    cik = ix.get_cik('INTC')

    indexer.download_xbrl_data(cik,from_year, to_year, 'All')
    Downloading file http://www.sec.gov/Archives/edgar/data/50863/000005086316000105/intc-20151226.xml
    To ./edgar/filings/intc-20151226.xml
    Downloading file http://www.sec.gov/Archives/edgar/data/50863/000005086316000125/intc-20160402.xml
    To ./edgar/filings/intc-20160402.xml
    Downloading file http://www.sec.gov/Archives/edgar/data/50863/000005086316000142/intc-20160702.xml
    To ./edgar/filings/intc-20160702.xml
    Downloading file http://www.sec.gov/Archives/edgar/data/50863/000005086316000153/intc-20161001.xml
    To ./edgar/filings/intc-20161001.xml








Credits
---------

This package was created with Cookiecutter_ and the `robren/cookiecutter-pypackage` a fork of
the `audreyr/cookiecutter-pypackage`_ project template.

.. _`robren/cookiecutter-pypackage`: https://github.com/robren/cookiecutter-pypackage
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

