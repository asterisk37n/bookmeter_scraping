#!/usr/bin/myenv/bin python
#-*- coding: UTF-8 -*-
import sqlite3
import os
import datetime
from flask import g

class Database():
    """
    Methods:
        select_all_books(): returns self.books, which is list of tuples.
        insert_row(items): items is dict, tuple, list of tuples or list of dicts.
        isnew(isbn): if scraped information is 10 minutes old oy younger.
        select_book(isbn): return row from table. If isbn is not in table, returns empty tuple ().

    (0,'isbn', 'text', 0, None, 1),
    (1, 'title', 'text', 0, None, 0),
    (2, 'author', 'text', 0, None, 0),
    (3, 'publisher', 'text', 0, None, 0),
    (4, 'new_price', 'integer', 0, None, 0),
    (5, 'used_price', 'integer', 0, None, 0),
    (6, 'price_ratio', 'real', 0, None, 0),
    (7, 'shipping', 'real', 0, None, 0),
    (8, 'detail_page', 'text', 0, None, 0),
    (9, 'thumbnail', 'text', 0, None, 0),
    (10, 'scraped_date', 'text', 0, None, 0)]
    """
    def __init__(self):
        self.DATABASE = os.path.join(os.path.dirname(__file__),'database','books.db')

    def connect(self, debug=False):
        if debug:
            self.conn = sqlite3.connect(self.DATABASE)
        else:
            self.conn = self.get_db()
        self.cur = self.conn.cursor()
        self.cur.execute('''create table if not exists books (
            isbn text primary key, title text, author text, publisher text,
            new_price integer, used_price integer, price_ratio real, shipping integer,
            detail_page text, thumbnail text, scraped_date text
        )''')
        self.get_column_names()

    def __str__(self):
        pass

    def insert_row(self, items):
        """ items is dict, tuple, list of tuples, or list of dicts"""
        def insert_dict(item):
            columns = self.get_column_names()
            values = tuple([item[column] for column in columns])
            self.cur.execute('INSERT OR REPLACE INTO books VALUES (?,?,?,?,?,?,?,?,?,?,?)', values)
        def insert_tuple(item):
            self.cur.execute('INSERT INTO books VALUES (?,?,?,?,?,?,?,?,?,?,?)', item)
#                print('Insert successful.')
        if isinstance(items,dict):
            insert_dict(items)
        elif isinstance(items,tuple):
            insert_tuple(items)
        elif isinstance(items,list):
            if isinstance(items[0],tuple):
                self.cur.executemany('INSERT INTO books VALUES (?,?,?,?,?,?,?,?,?,?,?)', items)
                print('Insert successful:', items)
            elif isinstance(items[0], dict):
                columns = self.get_column_names()
                values = [tuple(item[column] for column in columns) for item in items]
                self.cur.executemany('INSERT OR REPLACE INTO books VALUES (?,?,?,?,?,?,?,?,?,?,?)', values)
                print('Insert successful:', items)
        else:
            print('ERROR in inserting {}.'.format(items))

    def isnew(self, isbn):
        booktuple = self.select_book(isbn)
        if booktuple is None:
            print(isbn, booktuple, 'is None')
            return False
        else:
            scraped_datetime = datetime.datetime.strptime(booktuple[-1], '%Y-%m-%d %H:%M:%S.%f')
            if  scraped_datetime < datetime.datetime.now() < scraped_datetime + datetime.timedelta(days=1):
                return True
            else:
                return False

    def select_book(self, isbn):
        """ return a tuple of a row selected by isbn. """
        return self.cur.execute('SELECT * FROM books WHERE isbn=?', (isbn,)).fetchone()

    def select_book_dict(self, isbn):
        """ return a dict. if isbn does not exists in the table, returns empty dict, {}. """
        tpl = self.cur.execute('SELECT * FROM books WHERE isbn=?',(isbn,)).fetchone()
        book = {}
        for i, column in enumerate(self.column_names):
            book[column] = tpl[i]
        return book        

    def get_column_names(self):
        """ return list of names """
        pragma = self.cur.execute('PRAGMA table_info(books)')
        result = self.cur.fetchall()
        names = [i[1] for i in result]
        self.column_names = names 
        return names

    def get_isbn_iter(self):
        return iter(self.cur.execute('SELECT isbn FROM books').fetchall())

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()
 
    def get_db(self):
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(self.DATABASE)
        return db

#    @self.app.teardown_appcontext
    def close_connection(self, exception):
        self.conn.commit()
        self.cur.close()
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()
