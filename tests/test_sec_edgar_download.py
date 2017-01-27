#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_sec_edgar_download
----------------------------------

Tests for `sec_edgar_download` module.
"""

import os
import filecmp
import pytest
from sec_edgar_download  import indexer

@pytest.fixture
def response():
    """Sample pytest fixture.
    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_get_cik():
    cik = indexer.get_cik('intc')
    assert(cik == '0000050863')

def test_get_one_month_rss(tmpdir):
    print('tmpdir ={} '.format(tmpdir.dirname))
    ix = indexer.SecIndexer(tmpdir.dirname)
    ix.download_sec_feeds(2016,2016,12, 12)
    rss_file = os.path.join(ix.feed_dir,'xbrlrss-2016-12.xml')
    assert(filecmp.cmp('tests/xbrlrss-2016-12.xml',rss_file))

def test_get_10k(tmpdir):
    print('tmpdir ={} '.format(tmpdir.dirname))
    ix = indexer.SecIndexer(tmpdir.dirname)
    ix.download_sec_feeds(2016,2016,1, 2)
    cik = indexer.get_cik('intc')
    files = ix.download_xbrl_data(cik, 2016, 2016,form_type='10-K'  )
    xbrl_file_should_be = os.path.join(ix.filings_dir,'intc-20151226.xml')   
    assert(filecmp.cmp('tests/intc-20151226.xml',xbrl_file_should_be))


#def test_create_file(tmpdir):
#    p = tmpdir.mkdir("sub").join("hello.txt")
#    print('tmpdir = %s',tmpdir)
#    p.write("content")
#    assert p.read() == "content"
#    assert len(tmpdir.listdir()) == 1
    #assert 0
