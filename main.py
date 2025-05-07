from app import create_app
from flask import g

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

app.teardown_appcontext(close_db)  # app - экземпляр Flask-приложения