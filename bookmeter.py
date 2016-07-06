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
        self.last_page_number = -1
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
        isbns_in_page = [href[3:] for href in href_list if href.startswith('/b')]
        self._get_last_page_number(tree)
        return isbns_in_page

    def _get_last_page_number(self, tree):        
        page_navi_hedge = tree.xpath('//span[@class="page_navi_hedge"]/a/@href') # start or last link
        href = tree.xpath('//div[@class="page_navis"]')[0][-1][0].get('href')
        if not href.endswith('booklistpre') and self.last_page_number<0:
            self.last_page_number = int(href.split('=')[-1])
        else:
            pass
#        self.last_page_number = tree.xpath('//div[@class="page_navis"]')[0][-1][0].get('href')
#        if len(page_navi_hedge)==1: # if not contains end
#        else:
#        self.last_page_number = int(tree.xpath('//span[@class="page_navi_hedge"]/a/@href')[-1].split('=')[-1])
        print(self.last_page_number)
        return self.last_page_number

if __name__ == '__main__':
    bs = BookmeterScraping('104933')
    bs.get_isbns_in_page(1)
    bs.get_isbns_in_page(14)
    bs.get_isbns_in_page(15)
    bs.get_isbns_in_page(18)
