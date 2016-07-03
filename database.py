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
        self.select_all_books()

    def close(self):
        self.cur.close()
        self.conn.close()

    def __str__(self):
        pass

    def select_all_books(self):
        self.books = list(self.cur.execute('''SELECT * FROM books ORDER BY price_ratio ASC'''))
        return self.books
        
    def insert_row(self, items):
        """ items is dict, tuple, list of tuples, or list of dicts"""
        def insert_dict(item):
            columns = self.get_column_names()
            values = tuple([item[column] for column in columns])
            self.cur.execute('INSERT OR REPLACE INTO books VALUES (?,?,?,?,?,?,?,?,?,?,?)', values)
#            try: 
#                self.cur.execute('INSERT INTO books VALUES (?,?,?,?,?,?,?,?,?,?,?)', values)
#                print('Insert successful.')                
#            except sqlite3.IntegrityError as e:
#                self.cur.execute('REPLACE INTO books VALUES (?,?,?,?,?,?,?,?,?,?,?)', values)
#                print('Insert successful.')
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
            elif isinstance(items[0], dict):
#                [insert_dict(i) for i in itemsi
                columns = self.get_column_names()
                values = [tuple(item[column] for column in columns) for item in items]
                self.cur.executemany('INSERT OR REPLACE INTO books VALUES (?,?,?,?,?,?,?,?,?,?,?)', values)
        else:
            print('ERROR in inserting {}.'.format(items))
        self.select_all_books()

    def isnew(self, isbn):
        booktuple = self.select_book(isbn)
        if booktuple is None:
            return False
        else:
            scraped_datetime = datetime.datetime.strptime(booktuple[-1], '%Y-%m-%d %H:%M:%S.%f')
            if  scraped_datetime < datetime.datetime.now() < scraped_datetime + datetime.timedelta(minutes=60):
                return True
            else:
                return False
                  
    def select_book(self, isbn):
        """ return a tuple. If isbn does not exists in the table, returns empty tuple, (). """
        return self.cur.execute('SELECT * FROM books WHERE isbn=?',(isbn,)).fetchone()

    def get_column_names(self):
        """ return list of names """
        pragma = self.cur.execute('PRAGMA table_info(books)')
        result = self.cur.fetchall()
        names = [i[1] for i in result]
        return names

    def commit(self):
        self.conn.commit()

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
