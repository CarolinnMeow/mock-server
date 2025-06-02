from flask import Blueprint, jsonify, request, abort
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from flasgger import swag_from
import uuid
import logging
import re
from app.db import execute_query
from app.schemas.account import physical_account_schema, legal_account_schema
from app.config import (
    ACCOUNT_TYPES,
    HTTP_METHODS,
    RESPONSE_MESSAGES,
    HTTP_STATUS_CODES
)
from app.utils import log_endpoint, require_headers_and_echo

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

accounts_bp = Blueprint('accounts', __name__)

# Регулярное выражение для проверки UUID
UUID_PATTERN = re.compile(r'^[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}$', re.I)

def validate_uuid(account_id: str) -> None:
    """Валидация формата UUID"""
    if not UUID_PATTERN.match(account_id):
        logger.warning(f"Invalid UUID format: {account_id}")
        abort(HTTP_STATUS_CODES["BAD_REQUEST"],
              description=RESPONSE_MESSAGES.get("invalid_uuid", "Invalid account_id format"))

def safe_validate(data, schema):
    try:
        validate(data, schema)
        return None
    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return str(e)

def safe_db_query(query, params=(), commit=False):
    try:
        return execute_query(query, params, commit)
    except Exception as e:
        logger.error(f"DB error: {e}")
        abort(HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"],
              description=RESPONSE_MESSAGES["db_error"])

# === Эндпоинты для счетов физических лиц ===

@accounts_bp.route('/accounts-v1.3.3/', methods=HTTP_METHODS[:2])  # GET, POST
@swag_from('../docs/accounts.yml')
@log_endpoint
@require_headers_and_echo
def physical_accounts():
    if request.method == 'GET':
        cur = safe_db_query(
            'SELECT * FROM accounts WHERE type = ?',
            (ACCOUNT_TYPES["physical"],)
        )
        return jsonify([dict(row) for row in cur.fetchall()]), HTTP_STATUS_CODES["OK"]

    if request.method == 'POST':
        error = safe_validate(request.json, physical_account_schema)
        if error:
            return jsonify({
                "error": RESPONSE_MESSAGES["validation_error"],
                "message": error
            }), HTTP_STATUS_CODES["BAD_REQUEST"]

        account_id = str(uuid.uuid4())
        safe_db_query(
            '''INSERT INTO accounts (id, balance, currency, type, status, owner)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (
                account_id,
                request.json['balance'],
                request.json['currency'],
                ACCOUNT_TYPES["physical"],
                request.json['status'],
                request.json['owner']
            ),
            commit=True
        )
        cur = safe_db_query('SELECT * FROM accounts WHERE id = ?', (account_id,))
        return jsonify(dict(cur.fetchone())), HTTP_STATUS_CODES["CREATED"]

    return jsonify({"error": RESPONSE_MESSAGES["method_not_allowed"]}), HTTP_STATUS_CODES["METHOD_NOT_ALLOWED"]

@accounts_bp.route('/accounts-v1.3.3/<account_id>', methods=HTTP_METHODS)
@swag_from('../docs/accounts.yml')
@log_endpoint
@require_headers_and_echo
def physical_account(account_id):
    validate_uuid(account_id)  # Проверка UUID

    if request.method == 'GET':
        cur = safe_db_query(
            'SELECT * FROM accounts WHERE id = ? AND type = ?',
            (account_id, ACCOUNT_TYPES["physical"])
        )
        account = cur.fetchone()
        if not account:
            return jsonify({"error": RESPONSE_MESSAGES["not_found"]}), HTTP_STATUS_CODES["NOT_FOUND"]
        return jsonify(dict(account)), HTTP_STATUS_CODES["OK"]

    if request.method == 'PUT':
        error = safe_validate(request.json, physical_account_schema)
        if error:
            return jsonify({
                "error": RESPONSE_MESSAGES["validation_error"],
                "message": error
            }), HTTP_STATUS_CODES["BAD_REQUEST"]

        safe_db_query(
            '''UPDATE accounts SET balance = ?, currency = ?, status = ?, owner = ?
               WHERE id = ? AND type = ?''',
            (
                request.json['balance'],
                request.json['currency'],
                request.json['status'],
                request.json['owner'],
                account_id,
                ACCOUNT_TYPES["physical"]
            ),
            commit=True
        )
        return jsonify({"status": "updated"}), HTTP_STATUS_CODES["OK"]

    if request.method == 'DELETE':
        safe_db_query(
            'DELETE FROM accounts WHERE id = ? AND type = ?',
            (account_id, ACCOUNT_TYPES["physical"]),
            commit=True
        )
        return '', HTTP_STATUS_CODES["NO_CONTENT"]

    return jsonify({"error": RESPONSE_MESSAGES["method_not_allowed"]}), HTTP_STATUS_CODES["METHOD_NOT_ALLOWED"]

# === Эндпоинты для счетов юридических лиц ===

@accounts_bp.route('/accounts-le-v2.0.0/', methods=HTTP_METHODS[:2])  # GET, POST
@swag_from('../docs/accounts.yml')
@log_endpoint
@require_headers_and_echo
def legal_accounts():
    if request.method == 'GET':
        cur = safe_db_query(
            'SELECT * FROM accounts WHERE type = ?',
            (ACCOUNT_TYPES["legal"],)
        )
        return jsonify([dict(row) for row in cur.fetchall()]), HTTP_STATUS_CODES["OK"]

    if request.method == 'POST':
        error = safe_validate(request.json, legal_account_schema)
        if error:
            return jsonify({
                "error": RESPONSE_MESSAGES["validation_error"],
                "message": error
            }), HTTP_STATUS_CODES["BAD_REQUEST"]

        account_id = str(uuid.uuid4())
        safe_db_query(
            '''INSERT INTO accounts (id, balance, currency, type, status, company)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (
                account_id,
                request.json['balance'],
                request.json['currency'],
                ACCOUNT_TYPES["legal"],
                request.json['status'],
                request.json['company']
            ),
            commit=True
        )
        cur = safe_db_query('SELECT * FROM accounts WHERE id = ?', (account_id,))
        return jsonify(dict(cur.fetchone())), HTTP_STATUS_CODES["CREATED"]

    return jsonify({"error": RESPONSE_MESSAGES["method_not_allowed"]}), HTTP_STATUS_CODES["METHOD_NOT_ALLOWED"]

@accounts_bp.route('/accounts-le-v2.0.0/<account_id>', methods=HTTP_METHODS)
@swag_from('../docs/accounts.yml')
@log_endpoint
@require_headers_and_echo
def legal_account(account_id):
    validate_uuid(account_id)

    if request.method == 'GET':
        cur = safe_db_query(
            'SELECT * FROM accounts WHERE id = ? AND type = ?',
            (account_id, ACCOUNT_TYPES["legal"])
        )
        account = cur.fetchone()
        if not account:
            return jsonify({"error": RESPONSE_MESSAGES["not_found"]}), HTTP_STATUS_CODES["NOT_FOUND"]
        return jsonify(dict(account)), HTTP_STATUS_CODES["OK"]

    if request.method == 'PUT':
        error = safe_validate(request.json, legal_account_schema)
        if error:
            return jsonify({
                "error": RESPONSE_MESSAGES["validation_error"],
                "message": error
            }), HTTP_STATUS_CODES["BAD_REQUEST"]

        safe_db_query(
            '''UPDATE accounts SET balance = ?, currency = ?, status = ?, company = ?
               WHERE id = ? AND type = ?''',
            (
                request.json['balance'],
                request.json['currency'],
                request.json['status'],
                request.json['company'],
                account_id,
                ACCOUNT_TYPES["legal"]
            ),
            commit=True
        )
        return jsonify({"status": "updated"}), HTTP_STATUS_CODES["OK"]

    if request.method == 'DELETE':
        safe_db_query(
            'DELETE FROM accounts WHERE id = ? AND type = ?',
            (account_id, ACCOUNT_TYPES["legal"]),
            commit=True
        )
        return '', HTTP_STATUS_CODES["NO_CONTENT"]

    return jsonify({"error": RESPONSE_MESSAGES["method_not_allowed"]}), HTTP_STATUS_CODES["METHOD_NOT_ALLOWED"]
