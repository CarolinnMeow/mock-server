import sqlite3
from flask import g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('mockserver.db')
        g.db.row_factory = sqlite3.Row
    return g.db

def execute_query(query, args=(), commit=False):
    db = get_db()
    cur = db.execute(query, args)
    if commit:
        db.commit()
    return cur

def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()