#!/usr/bin/myenv python
#-*-coding: UTF-8-*-
from amazon_api import AmazonAPI
from database import Database
from flaskapp import loadkey
import lxml.html
import lxml.etree
import time

class UpdateDatabase():
    def __init__(self):
        aws_access_id, aws_secret_key = loadkey('/home/ec2-user/.aws/credentials/rootkey.csv')
        self.api = AmazonAPI(aws_access_id, aws_secret_key, 'asterisk37n-22')
    def update(self):
        db = Database()
        db.connect(debug=True) 
        isbns = db.get_isbn_gen()
        query_isbns=[]
        for isbn in isbns:
            query_isbns.append(isbn)
            if len(query_isbns) == 10:
                result = self.api.query_to_list_of_dicts(*query_isbns)
                db.insert_row(result)
                query_isbns=[]
                time.sleep(1)
            else:
                pass
        else:
            if query_isbns:
                result = self.api.query_to_list_of_dicts(*query_isbns)
                db.insert_row(result)
        db.commit()
        db.close()

if __name__=='__main__':
    update = UpdateDatabase()
    update.update()
