#!/usr/bin/myenv/bin python
#-*-coding: UTF-8-*-
import lxml
from lxml import etree
import lxml.html
import datetime
import requests
import time
import re
import grequests
from bs4 import BeautifulSoup

class BookmeterScraping():
    """
    """
    def __init__(self, bookmeter_ID):
        self.bookmeter_ID = bookmeter_ID if isinstance(bookmeter_ID, str) else str(bookmeter_ID)
        self.isbns_to_read = []
        self.last_page_number = -1
        self.endpoint = 'https://bookmeter.com'
    def get_isbns_to_read(self):
        """
            debug==True is for offline mode.
        """
        page=1
        while True:
            next_isbns = self.get_isbns_in_page(page)
            if next_isbns:
                self.isbns_to_read.extend(next_isbns)
                page+=1
                time.sleep(.5)
            else:
                break
        return self.isbns_to_read

    def get_isbns_in_page(self, page):
        url = 'https://bookmeter.com/users/{id}/books/wish?page={page}'.format(**{'id':self.bookmeter_ID, 'page':page})
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        divs = soup.findAll('div', class_='thumbnail__cover')
        urls = [self.endpoint + div.find('a')['href'] for div in divs]
        rs = (grequests.get(u) for u in urls)
        responses = grequests.map(rs)
        sources = (r.content for r in responses)
        hrefs = (BeautifulSoup(s, 'html.parser').find('a', target='_blank')['href'] for s in sources)
        isbns = ((lambda x: re.findall(r'\d{9}[\dX]',x)[0])(href) for href in hrefs)
        if page == 1:
            self._get_last_page_number(r.content)
        return isbns

    def _get_last_page_number(self, wishpage_source): 
        soup = BeautifulSoup(wishpage_source, 'html.parser')
        a = soup.findAll('a', class_='bm-pagination__link')
        if a: # if page has links to another page
            self.last_page_number = re.findall(r'\d+$', a[-1]['href'])[-1]
        else:
            self.last_page_number = 1
        return self.last_page_number

if __name__ == '__main__':
    bs = BookmeterScraping('107634')
    isbns = bs.get_isbns_in_page(1)
    print(list(isbns))
    bs = BookmeterScraping('104933')
    isbns = bs.get_isbns_in_page(1)
    print(list(isbns))
