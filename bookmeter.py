#!/usr/bin/myenv/bin python
#-*-coding: UTF-8-*-
import lxml
from lxml import etree
import lxml.html
import datetime
import requests
import time

class BookmeterScraping():
    """
    Methods:
        get_isbns_to_read(debug=False): set and return self.isbns_to_read
        _get_isbn_from_URL(url)
    """
    def __init__(self, bookmeter_ID):
        self.bookmeter_ID = bookmeter_ID if isinstance(bookmeter_ID, str) else str(bookmeter_ID)
        self.isbns_to_read = []
    
    def get_isbns_to_read(self, debug=False):
        """
            debug==True is for offline mode.
        """
        if debug == True:
            self.isbns_to_read = ['479422155X', '4622076519', '4062579359', '4062183765', '4822249417', '4797338121',
                             '439313544X', '4166601741', '4569697135', '486182334X', '483345002X', '4062883600']
            return self.isbns_to_read
        page=1
        while True:
            next_isbns = self.get_isbns_in_page(page)
            if next_isbns:
                self.isbns_to_read.extend(next_isbns)
                page+=1
                time.sleep(.5)
            else:
                break
        print(self.isbns_to_read)
        return self.isbns_to_read

    def get_isbns_in_page(self, page):
        url = 'http://bookmeter.com/u/{id}/booklistpre&p={page}'.format(**{'id':self.bookmeter_ID, 'page':page})
        isbns_in_page = self._get_isbn_from_URL(url)
        return isbns_in_page
        

    def _get_isbn_from_URL(self, url):
        page = requests.get(url)
        tree = lxml.html.fromstring(page.content)
        href_list = tree.xpath('//div[@class="book_box_book_title"]/a/@href')
        ISBN10_in_page = [href[3:] for href in href_list if href.startswith('/b')]
        return ISBN10_in_page
    
if __name__ == '__main__':
    bs = BookmeterScraping('104933')
    isbns = bs.get_isbns_to_read(debug=True)
    print(isbns)