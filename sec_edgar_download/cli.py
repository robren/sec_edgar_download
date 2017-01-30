#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# from  sec_edgar_download import download_sec_feeds

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
# the imports have to be under the docstring
# otherwise the docopt module does not work.
from docopt import docopt
from sec_edgar_download import indexer as ix 


def main(args=None):
    arguments = docopt(__doc__, version='sec_edgar_download 0.0.0')
    print(arguments)

    from_year = int(arguments['<from-year>'])
    to_year = int(arguments['<to-year>'])

    work_dir = arguments['--wd']
    if work_dir is None:
        work_dir = './edgar'

    if arguments['getrss']:
        from_month = arguments['--fm']
        if from_month is not None:
            from_month = int(from_month)
        else:
            from_month = 1

        to_month = arguments['--tm']
        if to_month is not None:
            to_month = int(to_month)
        else:
            to_month = 12

        indexer = ix.SecIndexer(work_dir)
        indexer.download_sec_feeds(from_year, to_year, from_month, to_month)

    elif arguments['getxbrl']:
        cik = arguments['--cik']
        if cik is not None:
            cik = int(cik)
        ticker = arguments['--ticker']
        if ticker is not None:
            cik = ix.get_cik(ticker)

        form_type = arguments['--ft']

        indexer = ix.SecIndexer(work_dir)
        indexer.download_xbrl_data(cik, from_year, to_year, form_type)


if __name__ == '__main__':
    main()
