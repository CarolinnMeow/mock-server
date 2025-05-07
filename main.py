from app import create_app
from flask import g
from app.db import get_db, close_db

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

app.teardown_appcontext(close_db)  # app - экземпляр Flask-приложения

@app.cli.command('init-db')
def init_db():
    db = get_db()
    with open('schema.sql', 'r') as f:
        db.executescript(f.read())
    print("Database initialized")