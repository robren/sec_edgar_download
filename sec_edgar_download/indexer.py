"""This module provides functions to download and index edgar sec RSS
feeds and to download individual filers xbrl filings

:copyright: (c) 2017 by Robert Rennison
:license: Apache 2, see LICENCE for more details
"""

import os
import os.path
import sqlite3 as sqlite3
import logging
import re
import pandas as pd
from lxml import etree
import requests
from bs4 import BeautifulSoup


def get_cik(ticker):
    """ Query the edgar site for the cik corresponding to a ticker.
    Returns a string representing the cik.
    By using the xml output format in the query and BeautifulSoup
    the parsing of the cik from the response is simple; avoiding
    the need for regexps
    """

    url = 'https://www.sec.gov/cgi-bin/browse-edgar'
    query_args = {'CIK': ticker, 'action': 'getcompany', 'output': 'xml'}
    response = requests.get(url, params=query_args)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup.cik.get_text()


def _parse_xbrlfiles(edgar_sub_elem, edgar_ns, item):

    ed_xbrl = './/edgar:' + 'xbrlFile'
    xbrl_files = edgar_sub_elem.findall(ed_xbrl, namespaces=edgar_ns)
    xml_filing_found = False
    xbrl_url = None
    for xbrl_file in xbrl_files:
        xbrl_type = xbrl_file.attrib['{http://www.sec.gov/Archives/edgar}type']
        if xbrl_type == "EX-101.INS" or xbrl_type == 'EX-100.INS':
            xbrl_url = \
                    xbrl_file.attrib['{http://www.sec.gov/Archives/edgar}url']
            xml_filing_found = True
            break
    if xml_filing_found is False:
        item_title = item.find('title')
        logging.warning('No EX-101 or EX-100 xml files found for  %s',
                        item_title.text)

    return xbrl_url


def _month_year_iter(from_year, to_year, from_month, to_month):
    ym_from = 12 * from_year + from_month - 1
    ym_to = 12 * to_year + to_month
    for yearm in range(ym_from, ym_to):
        year, month = divmod(yearm, 12)
        yield year, month + 1

# TODO
# Check on classname syntax
# finish of classifying
# correct logging


class SecIndexer():
    def __init__(self, work_dir="edgar/"):
        self.work_dir = work_dir
        self.database = os.path.join(self.work_dir, 'edgar.db')
        self.feed_dir = os.path.join(self.work_dir, 'rss-archives')
        self.filings_dir = os.path.join(self.work_dir, 'filings')

        self.edgar_keys = (
            'company_name', 'form_type', 'filing_date', 'cik_number',
            'accession_number', 'file_number', 'acceptance_datetime',
            'period', 'assistant_director', 'assigned_sic', 'fiscal_year_end',
            'xbrl_files'
            )

        self.edgar_labels = (
            'companyName', 'formType', 'filingDate', 'cikNumber',
            'accessionNumber', 'fileNumber', 'acceptanceDatetime',
            'period', 'assistantDirector', 'assignedSic', 'fiscalYearEnd',
            'xbrlFiles'
        )

        # FIXME, need to use a private logger not the root one.
        # logging.basicConfig(filename='logging.log',level=logging.DEBUG)
        logging.basicConfig(level=logging.INFO)

        self._prep_directories()
        self._prep_database_table()

    def download_sec_feeds(self, from_year, to_year,
                           from_month=1, to_month=12):
        """Downloads and parses Edgar RSS feeds

        Downloads and parses RSS feeds for the range of dates given. The
        parsed feeds are stored in a mysqlite3 database.

        Args:
        from_year (int): The start year to begin downloading feeds from.
        to_year (int): The end  year for which feeds are desired.
        from_month (int): The start month for feeds.
        to_month (int): The end month for feeds.

        Dates are inclusive

        Returns:
        None
        """
        dicts = []

        for year, month in _month_year_iter(from_year, to_year,
                                            from_month, to_month):
            filename = self._download_sec_feed(year, month)
            edgar_dict = self.parse_sec_rss_feeds(filename)
            dicts.append(edgar_dict)

        self._save_dicts_to_database(dicts)

    def download_xbrl_data(self, cik, from_year, to_year, form_type='All'):
        """Downloads xbrl filing data from the SEC edgar website

        Requires that the user has previously downloaded and indexed the feeds
        for the period in question using the CLI to invoke
        download_sec_feeds().  Downloads files to the subdirectory "filings"
        within the directory set by the work_dir class variable. This defaults
        to "./edgar" within the directory the application is running in.

        Args:
            cik (str): The SEC CIK number associatd with the filer.
            from_year (int): Beginning year to download filings from.
            to_year (int): Ending year for forms download.
            form_type (str: "10-K", "10-Q" or "All" (defaults to "All")

        """
        logging.debug('download_xbrl_data: cik = %s, form_type = %s,'
                      'from_year = %d, to_year = %d', cik, form_type,
                      from_year, to_year)

        conn = sqlite3.connect(self.database)
        df = pd.read_sql('SELECT * from feeds', conn)
        df.head()

        df['filing_date'] = pd.to_datetime(
                                df['filing_date'],
                                format='%m/%d/%Y')

        # TODO maybe allow from month and to month
        from_date = str(from_year) + '-01-01'
        to_date = str(to_year) + '-12-31'

        if form_type == 'All':
            mask = (df['filing_date'] >= from_date) \
                   & (df['filing_date'] <= to_date) \
                   & (df['cik_number'] == cik)

        else:
            mask = (df['filing_date'] >= from_date) \
                   & (df['filing_date'] <= to_date) \
                   & (df['cik_number'] == cik) \
                   & (df['form_type'] == form_type)

        masked_df = df.loc[mask]

        for url in masked_df['xbrl_files']:
            print('Downloading file {}'.format(url))
            filename = os.path.join(self.filings_dir, os.path.basename(url))
            print('To {}'.format(filename))
            response = requests.get(url)
            with open(filename, 'w') as f:
                f.write(response.text)

                logging.debug('download_xbrl_data: found %d filings wrote to\
                        %s', len(masked_df), filename)

    def _download_sec_feed(self, year, month):
        """Download an SEC RSS feed for a specifc month of a given year

        Downloads RSS feeds from the SEC edgar website for a given year and
        month.  The feeds are stored by year and month, each containing
        details of all of the filings made to the SEC for that month

        Args:
            year (int); The year of the feed
            month (int); The year of the feed

        Returns:
            feed_file (str): The location of the downloaded RSS file.

        """
        logging.debug('download_sec_feed: year = %d, month = %d', year, month)

        feed_filename = ('xbrlrss-' + str(year) +
                         '-' + '{:02}'.format(month) + '.xml')
        logging.debug('feed_filename = %s', feed_filename)

        feed_file = os.path.join(self.feed_dir, feed_filename)

        if not os.path.exists(feed_file):
            edgar_filings_feed = ('http://www.sec.gov/Archives/edgar/monthly/'
                                  + feed_filename)
            logging.debug('Edgar Filings Feed = %s', edgar_filings_feed)

            response = None
            try:
                response = requests.get(edgar_filings_feed, timeout=4)
                response.raise_for_status()
            except requests.exceptions.RequestException as err:
                logging.exception("RequestException:%s", err)
                #os.sys.exit(1)

            with open(feed_file, 'w') as file:
                file.write(response.text)

            logging.info('Downloaded RSS feed: %s', feed_file)

        else:
            logging.debug('Skipping download:'
                          'RSS feed %s already downloaded', feed_file)

        return feed_file

    def parse_sec_rss_feeds(self, rss_filename):
        """ Parses an Edgar RSS feed into a dict

        Parses and Edgar RSS feed, looking for details of corporate filings.
        Extracts the details from each filer, including the URL reference to
        the actual xbrl format filing itself. Each feedfile contains the
        details of a months worth of filings for all filers.

        The xbrl filing for each filer is NOT downloaded.

        Args:
        rss_filename (str): A local copy of the RSS feed file.

        Returns:
        edgar_dict (Dict): A dictionary containing the details as filed
        by each filer. The keys for this dictionary are described by the
        class variable edgar_keys.

        """
        logging.info("Parsing RSS feed %s", rss_filename)

        root = etree.parse(rss_filename).getroot()
        # 'items' elements contain the filing details for each company listed
        items = list(root.iter('item'))
        logging.debug('%d items found in RSS feed', len(items))

        edgar_dict = {edgar_key: [] for edgar_key in self.edgar_keys}
        edgar_ns = {'edgar': 'http://www.sec.gov/Archives/edgar'}
        for item in items:
            for key, label in zip(self.edgar_keys, self.edgar_labels):
                edgar_sub_elem = item.find('.//edgar:' +
                                           label, namespaces=edgar_ns)
                if edgar_sub_elem is None:
                    edgar_dict[key].append(None)
                    continue
                # logging.debug('tag = %s',edgar_sub_elem.tag)
                # xbrlfiles contains the URLs of the actual filings
                if 'xbrlFiles' in edgar_sub_elem.tag:
                    assert label == 'xbrlFiles'
                    xbrl_url = _parse_xbrlfiles(edgar_sub_elem, edgar_ns, item)
                    edgar_dict[key].append(xbrl_url)
                else:
                 #  logging.debug('text =  %s',edgar_sub_elem.text)
                    edgar_dict[key].append(edgar_sub_elem.text)

        return edgar_dict

    def _prep_directories(self):
        """ Creates the FEEDS and the FILINGS directories"""

        if not os.path.isdir(self.feed_dir):
            os.makedirs(self.feed_dir)
            logging.debug('Created new directory %s', self.feed_dir)

        if not os.path.isdir(self.filings_dir):
            os.makedirs(self.filings_dir)
            logging.debug('Created new directory %s', self.filings_dir)

    def _prep_database_table(self):
        """
        Creates a "feeds" table in a sqllite2 database. Sets the PRIMARY KEY
        to be the accession_number.

        To ensure that the  accesson_number is marked  as a PRIMARY KEY we
        need to manually create the db table. Pandas does not create a table
        with a PRIMARY KEY; without ths, repeated updates from subequent runs
        on the same feed would cause the database to get duplicate entries and
        grow!
        """

        columns = ','.join(self.edgar_keys)
        columns = re.sub('accession_number',
                         'accession_number PRIMARY KEY',
                         columns)
        table_parms = ('''CREATE TABLE IF NOT EXISTS feeds ({})'''
                       .format(columns))
        conn = sqlite3.connect(self.database)
        curr = conn.cursor()
        curr.execute(table_parms)
        conn.commit()
        conn.close()

    def _save_dicts_to_database(self, dicts):
        """
        Takes a list of dictionaries, converts to a pandas dataframe then
        stores this into a sqlite3 database
        """
        d_frames = []
        for dic in dicts:
            df = pd.DataFrame(dic)
            d_frames.append(df)

        db_df = pd.concat(d_frames)

        # deduplicate
        len_before = len(db_df)
        db_df.drop_duplicates('accession_number', inplace=True)
        len_after = len(db_df)
        dropped = len_before - len_after
        if dropped:
            logging.info('Dropped %d duplicates', dropped)

        db_df.set_index('accession_number', inplace=True)
        conn = sqlite3.connect(self.database)
    #   conn.set_trace_callback(print)

        db_df.to_sql("feeds", conn, if_exists="replace", chunksize=1000)
        logging.info('%d items parsed', len(db_df))
        logging.info('Saved feed details to %s\n', self.database)
