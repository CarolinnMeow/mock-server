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

def execute_query(query, args=()):
    return get_db().execute(query, args)

@system_bp.route('/')
def index():
    return jsonify({
        "message": "Mock Server API",
        "version": "1.0.0",
        "endpoints": {
            "accounts (physical)": "/accounts-v1.3.3/",
            "accounts (legal)": "/accounts-le-v2.0.0/",
            "payments": "/payments-v1.3.1/",
            "pm_211fz": "/pm-211fz-v1.3.1/",
            "consents (physical)": "/consent-pe-v2.0.0/",
            "consents (legal)": "/consent-le-v2.0.0/",
            "documents (bank)": "/bank-doc-v1.0.1/",
            "documents (insurance)": "/insurance-doc-v1.0.1/",
            "vrp": "/vrp-v1.3.1/",
            "transactions": "/transaction-history-v1.0.0/",
            "medical insured": "/medical-insured-person-v3.0.3/",
            "product agreements": "/product-agreement-consents-v1.0.1/",
            "metrics": "/metrics",
            "health": "/health"
        }
    })

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
