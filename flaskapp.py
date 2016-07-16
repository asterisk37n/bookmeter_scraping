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

# @app.route('/')
# def index():
#    return 'Index Page'

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        bookmeter_id = request.form['id'].strip()
        if bookmeter_id.endswith('/'):
            bookmeter_id = bookmeter_id[:-1]
        if not bookmeter_id.startswith('http://bookmeter.com/u/'):
            return render_template('login.html', msg='URL {} is incorrect.'.format(request.form['id']))
        session['id'] = bookmeter_id.replace('http://bookmeter.com/u/', '')
        print(session['id'])
        return redirect(url_for('ab', bookmeter_id=session['id']))
    return render_template('login.html')

def loadkey(path):
    with open(path) as f:
        reader = csv.reader(f)
        tmplist = []
        for line in reader:
            tmplist.append(line)
    AWS_access_key_id = tmplist[0][0].split('=')[1]
    AWS_secret_key = tmplist[1][0].split('=')[1]
    return AWS_access_key_id, AWS_secret_key
       

@app.route('/ab/<bookmeter_id>', methods=['GET', 'POST'])
@app.route('/ab/<bookmeter_id>/<page>', methods=['GET', 'POST'])
def ab(bookmeter_id, page=None):
    if page is None:
        page=1
    starttime = time.time()
    bs = BookmeterScraping(bookmeter_id)
    db = Database()
    db.connect(debug=False)
    aws_access_id, aws_secret_key = loadkey('/home/ec2-user/.aws/credentials/rootkey.csv')
    api = AmazonAPI(aws_access_id, aws_secret_key, 'asterisk37n-22')
    show_isbns = iter(bs.get_isbns_in_page(page=page))
    visible_books = []
    query_isbns=[]
    time1 = time.time()
    print('finished scraping', time1-starttime)
    for isbn in show_isbns:
        if db.isnew(isbn):
            visible_books.append(db.select_book_dict(isbn))
        else: 
            query_isbns.append(isbn)
            if len(query_isbns) == 10:
                result = api.query_to_list_of_dicts(*query_isbns)
                visible_books.extend(result)
                db.insert_row(result)
                query_isbns=[]
            else:
                pass
    else:
        if query_isbns:
            result = api.query_to_list_of_dicts(*query_isbns)
            visible_books.extend(result)
            db.insert_row(result)
    db.commit()
    db.close()
    print('for loop', time.time()-time1)
    books_shown = visible_books
    for i in books_shown:
        i['reasonable'] = 0<i['used_price']<=100 or 0<=i['price_ratio']<=0.01
        i['new_price'] = '{:,d}'.format(i['new_price']) if i['new_price'] >0 else ' - '
        i['used_price'] = '{:,d}'.format(i['used_price']) if i['used_price'] >0 else ' - '
    @after_this_request
    def update_database(response):
        return response
        
    start, end = link_range(page, bs.last_page_number)
    return render_template('ab.html', books=books_shown, page=int(page), last_page_number=bs.last_page_number, bookmeter_id=bookmeter_id, start=start, end=end)

def link_range(page, last):
    page, last = int(page), int(last)
    if last<11:
        return 1,last
    else:
        if page<=6:
            return 1,10
        elif page<=last-4:
            return page-5, page+4
        else:
            return last-9, last
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
