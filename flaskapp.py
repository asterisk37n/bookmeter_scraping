#!/usr/bin/myenv python
#-*-coding: UTF-8-*-
from flask import Flask, render_template, redirect, url_for, request, session, g
import datetime
import numpy as np
import csv
from bookmeter import BookmeterScraping
from amazon_api import AmazonAPI
from database import Database
import time
import os

app = Flask(__name__)

@app.route('/')
def index():
    return 'Index Page'

@app.route('/login', methods=['GET', 'POST'])
def login():
    print(request.method)
    if request.method == 'POST':
        if not request.form['id'].startswith('http://bookmeter.com/u/'):
            print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
            return render_template('login.html', msg='URL is incorrect.')
        session['id'] = request.form['id'].replace('http://bookmeter.com/u/', '')
        return redirect(url_for('ab', bookmeter_id=session['id']))
    return render_template('login.html')

def loadkey(path):
    print('home', os.path.isdir('/home/ec2-user/'))
    print('.aws',os.path.isdir('/home/ec2-user/.aws'))
    print('credentials',os.path.exists('/home/ec2-user/.aws/credentials'))
#    print('key', open('/home/ec2-user/.aws/credentials/rootkey.csv').read())
    with open(path) as f:
        reader = csv.reader(f)
        tmplist = []
        for line in reader:
            tmplist.append(line)
    AWS_access_key_id = tmplist[0][0].split('=')[1]
    AWS_secret_key = tmplist[1][0].split('=')[1]
    return AWS_access_key_id, AWS_secret_key
       

@app.route('/ab/<bookmeter_id>', methods=['GET', 'POST'])
def ab(bookmeter_id):
#    if 'id' not in session:
#        return 'You are not logged in'
    starttime = time.time()
    bs = BookmeterScraping(bookmeter_id)
    db = Database()
    db.connect(debug=False)
    aws_access_id, aws_secret_key = loadkey('/home/ec2-user/.aws/credentials/rootkey.csv')
    api = AmazonAPI(aws_access_id, aws_secret_key, 'asterisk37n-22')
    isbns = bs.get_isbns_in_page(page=1)
    isbns.extend(bs.get_isbns_in_page(page=2))
    first_show_isbns = iter(isbns[:100])
    visible_books = []
    query_isbns=[]
    time1 = time.time()
    print('finished scraping', time1-starttime)
    for isbn in first_show_isbns:
        if db.isnew(isbn):
            book = {}
            row_tuple = db.select_book(isbn)
            for i, column in enumerate(db.get_column_names()):
                book[column] = row_tuple[i]
            visible_books.append(book)
            print('NEW',isbn)
        else: 
            query_isbns.append(isbn)
            if len(query_isbns) == 10:
                print('query sent:', query_isbns)
                result = api.query_to_list_of_dicts(*query_isbns)
                visible_books.extend(result)
                db.insert_row(result)
                query_isbns=[]
            else:
                pass
#        print('ISBN=', isbn, 'VISIBLE=',visible_books, 'QUERY=',query_isbns)
    else:
        if query_isbns:
            result = api.query_to_list_of_dicts(*query_isbns)
            visible_books.extend(result)
            db.insert_row(result)
    db.close()
    visible_books_currency=[]
    for i in visible_books:
        try:
#            i['new_price'] = '{:,d}'.format(int(i['new_price'])) if int(i['new_price']) >=0 else '-'
            pass
        except (ValueError, TypeError) as e:
            i['new_price'] = '-'
            print(e, i)
        try:
#            i['used_price'] = '{:,d}'.format(int(i['used_price']))  if int(i['used_price']) >=0 else '-'
            pass
        except (ValueError, TypeError) as e: 
            i['used_price'] = '-'
            print(e, i)
#        i['price_ratio'] = '-' if i['price_ratio']<0 else i['price_ratio']
        visible_books_currency.append(i)
    time2 = time.time()
    print('for loop', time2-time1)
    @after_this_request
    def update_database(response):
        return response
        
    return render_template('ab.html', books=visible_books_currency)

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return 'Post %d' % post_id

@app.route('/projects/')
def projects():
    return 'The project page'

@app.route('/about')
def about():
    return 'The about page'

def after_this_request(f):
    if not hasattr(g, 'after_request_callbacks'):
        g.after_request_callbacks = []
    g.after_request_callbacks.append(f)
    return f

@app.after_request
def per_request_callbacks(response):
    for func in getattr(g, 'call_after_request', ()):
        response = func(response)
    return response

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == "__main__":
    app.run()
