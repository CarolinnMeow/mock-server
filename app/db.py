import sqlite3
import click
from flask import current_app, g, abort

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def execute_query(query, args=(), commit=False):
    db = get_db()
    cur = db.execute(query, args)
    if commit:
        db.commit()
    return cur

def init_db(db=None, db_path=None):
    close = False
    if db is None:
        if db_path is not None:
            db = sqlite3.connect(db_path)
            close = True
        else:
            # Получаем путь к базе из Flask config
            db = sqlite3.connect(current_app.config['DATABASE'])
            close = True
    try:
        with open('schema.sql', 'r', encoding='utf-8') as f:
            db.executescript(f.read())
    except FileNotFoundError:
        print("Ошибка: файл schema.sql не найден в корне проекта!")
        exit(1)
    if close:
        db.close()

def safe_db_query(query, params=(), commit=False):
    import logging
    logger = logging.getLogger(__name__)
    try:
        return execute_query(query, params, commit)
    except Exception as e:
        logger.error(f"DB error: {e}")
        abort(500, description="Database error")

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('База данных инициализирована.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
