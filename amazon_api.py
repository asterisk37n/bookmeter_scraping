#!/usr/bin/myenv/bin python
#-*-coding: UTF-8-*-
from lxml import html
from lxml import etree
import numpy as np
import datetime
import requests
import hmac
from urllib.parse import quote
from urllib.parse import urlencode
import hashlib
import base64

class AmazonAPI():
    """
        Methods:
	item_lookup(*itemid)
	book_fromxml(xml=None)
	_calculate_ratio(new_price, used_price)
	_get_shipping(isbn)
    """
    def __init__(self, access_key, secret_key, associate_tag):
        self.access_key = access_key
        self.secret_key = secret_key
        self.accociate_tag = associate_tag
        self.books = []
        
    # def load_aws_keys(self, filename='rootkey.csv'):
    #     with open(filename, newline='') as f:
    #         reader = csv.reader(f)
    #         aws_keys = []
    #         for row in reader:
    #             key, value = row[0].split('=')
    #             aws_keys.append(value)
    #         self.access_key, self.secret_key = aws_keys[0], aws_keys[1]
    #         return (self.access_key, self.secret_key)
        
    def item_lookup(self, *itemid):
        verb = 'GET'
        endpoint = 'http://webservices.amazon.co.jp/onca/xml'
        if self.access_key is None or self.secret_key is None:
            print('No access key is available.')
            sys.exit()
        asin = ','.join([str(i) for i in itemid])
        query_dict = {'AWSAccessKeyId':self.access_key,
                      'AssociateTag':'asterisk37n-22',
                      'IdType':'ASIN',
                      'ItemId':asin,
                      'Operation':'ItemLookup',
                      'ResponseGroup':'Images,ItemAttributes,Offers',
                      'Service':'AWSECommerceService',
                      'Timestamp':datetime.datetime.utcnow().isoformat(),
                      'Version':'2013-08-01'}
        sorted_query = sorted(query_dict.items())
        query_url = urlencode(sorted_query)
        msg_HMAC_SHA256 = verb + '\n' + 'webservices.amazon.co.jp' + '\n' + '/onca/xml' +'\n' + query_url # calcurate signature
        dig = hmac.new(self.secret_key.encode('utf-8'), msg=msg_HMAC_SHA256.encode('utf-8'), digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(dig).decode()      # py3k-mode
        request_url = endpoint + '?' + query_url+'&Signature='+quote(signature)
        self.r = requests.get(request_url)
        print('Response code: {}; URL={}; itemid={}'.format(self.r.status_code, request_url, itemid))
        return self.r 
    
    def book_fromxml(self, xml=None):
        """ returns a list of dicts """
        if xml==None:
            xml = self.r.text 
        root = etree.fromstring(xml)
        ns = 'http://webservices.amazon.com/AWSECommerceService/2013-08-01'
        self.books_in_xml = []        
        for item in root.findall('.//ns:Items/ns:Item', namespaces={'ns':ns}):
            try:isbn = item.find('.//ns:ItemAttributes/ns:ISBN', namespaces={'ns':ns}).text
            except:isbn = '';print('ISBN')
            try:title = item.find('.//ns:ItemAttributes/ns:Title', namespaces={'ns':ns}).text
            except:title = '';print('title')
            try:author = item.find('.//ns:ItemAttributes/ns:Author', namespaces={'ns':ns}).text
            except:author = '';print('author')
            try:publisher = item.find('.//ns:ItemAttributes/ns:Publisher', namespaces={'ns':ns}).text
            except:publisher = '';print('pub')
            try:new_price = int(item.find('.//ns:OfferSummary/ns:LowestNewPrice/ns:Amount', namespaces={'ns':ns}).text)
            except:new_price = -1;print('nprice')
            try:used_price = int(item.find('.//ns:OfferSummary/ns:LowestUsedPrice/ns:Amount', namespaces={'ns':ns}).text)
            except:used_price = -1;print('uprice')
            try:thumbnail = item.find('.//ns:ImageSets/ns:ImageSet[@Category="primary"]/ns:ThumbnailImage/ns:URL', namespaces={'ns':ns}).text
            except:thumbnail = '';print('thumbnail')
            try:detail_page = item.find('.//ns:DetailPageURL', namespaces={'ns':ns}).text
            except:detail_page = ''
            price_ratio = self._calculate_price_ratio(new_price, used_price)
            try:shipping = self._get_shipping(isbn)
            except:shipping = np.nan
            scraped_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            book_dict = {'isbn':isbn, 'title':title, 'author':author,'publisher':publisher,
                         'new_price':new_price, 'used_price':used_price, 'thumbnail':thumbnail,
                         'price_ratio':price_ratio, 'shipping':shipping, 'scraped_date':scraped_date, 'detail_page':detail_page}
            self.books_in_xml.append(book_dict)
#            print(self.books_in_xml)
        self.books.extend(self.books_in_xml)
        return self.books_in_xml

    def query_to_list_of_dicts(self, *query_isbns):
        req = self.item_lookup(*query_isbns)
        while req.status_code != 200:
            req = self.item_lookup(*query_isbns)
        xml = req.text
        result = self.book_fromxml(xml)
        return result
    
    def _calculate_price_ratio(self, new_price, used_price):
        price_ratio = round(used_price/new_price, 3) if new_price > 0 and used_price > 0 else -1.0
        return price_ratio
        
    def _get_shipping(self, isbn):
        if not isinstance(isbn, str):
            isbn = str(isbn)
        url = 'http://www.amazon.co.jp/gp/offer-listing/%s' % isbn
        page = requests.get(url)
        tree = html.fromstring(page.content)
        shipping_text = tree.xpath('//span[@class="olpShippingPrice"]/text()')
        shipping = np.nan
        if shipping_text:
            shipping = int(''.join([i for i in shipping_text[0] if i.isdigit()]))
        return shipping
