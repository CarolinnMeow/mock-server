from flask import Blueprint, jsonify, request, abort, g
from datetime import datetime
import psutil
import sqlite3

system_bp = Blueprint('system', __name__)
DATABASE = 'mockserver.db'


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@system_bp.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def execute_query(query, args=()):
    return get_db().execute(query, args)


@system_bp.route('/simulate-errors', methods=['GET'])
def simulate_errors():
    error_code = request.args.get('code', '500')
    abort(int(error_code))


@system_bp.route('/health', methods=['GET'])
def health_check():
    # Проверка подключения к БД
    try:
        execute_query('SELECT 1').fetchone()
        db_status = "connected"
    except sqlite3.Error:
        db_status = "disconnected"

    return jsonify({
        "status": "OK",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "database": db_status,
            "auth_service": "active"
        }
    })


@system_bp.route('/metrics', methods=['GET'])
def metrics():
    # Количество транзакций
    transactions_count = execute_query('SELECT COUNT(*) FROM transactions').fetchone()[0]

    # Количество счетов
    physical_accounts = execute_query(
        'SELECT COUNT(*) FROM accounts WHERE type = ?',
        ('physical_entity',)
    ).fetchone()[0]

    legal_accounts = execute_query(
        'SELECT COUNT(*) FROM accounts WHERE type = ?',
        ('legal_entity',)
    ).fetchone()[0]

    return jsonify({
        "requests_total": transactions_count,
        "accounts": {
            "physical": physical_accounts,
            "legal": legal_accounts
        },
        "memory_usage": f"{psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB"
    })
