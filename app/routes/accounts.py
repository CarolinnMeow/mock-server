from flask import Blueprint, jsonify, request, abort
from flask_api import status
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from flasgger import swag_from
import uuid
import logging
from app.db import execute_query
from app.schemas.account import physical_account_schema, legal_account_schema
from app.config import ACCOUNT_TYPES, HTTP_METHODS, RESPONSE_MESSAGES

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

accounts_bp = Blueprint('accounts', __name__)

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
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR, description=RESPONSE_MESSAGES["db_error"])

@accounts_bp.route('/accounts-v1.3.3/', methods=['GET', 'POST'])
@swag_from('../docs/accounts.yml')
def physical_accounts():
    logger.info(f"{request.method} {request.path}")
    if request.method == 'GET':
        cur = safe_db_query(
            'SELECT * FROM accounts WHERE type = ?',
            (ACCOUNT_TYPES["physical"],)
        )
        return jsonify([dict(row) for row in cur.fetchall()]), status.HTTP_200_OK

    if request.method == 'POST':
        error = safe_validate(request.json, physical_account_schema)
        if error:
            return jsonify({"error": RESPONSE_MESSAGES["validation_error"], "message": error}), status.HTTP_400_BAD_REQUEST

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
        return jsonify(dict(cur.fetchone())), status.HTTP_201_CREATED

    return jsonify({"error": RESPONSE_MESSAGES["method_not_allowed"]}), status.HTTP_405_METHOD_NOT_ALLOWED

@accounts_bp.route('/accounts-v1.3.3/<account_id>', methods=['GET', 'PUT', 'DELETE'])
@swag_from('../docs/accounts.yml')
def physical_account(account_id):
    logger.info(f"{request.method} {request.path} | id={account_id}")
    if request.method == 'GET':
        cur = safe_db_query(
            'SELECT * FROM accounts WHERE id = ? AND type = ?',
            (account_id, ACCOUNT_TYPES["physical"])
        )
        account = cur.fetchone()
        if not account:
            return jsonify({"error": RESPONSE_MESSAGES["not_found"]}), status.HTTP_404_NOT_FOUND
        return jsonify(dict(account)), status.HTTP_200_OK

    if request.method == 'PUT':
        error = safe_validate(request.json, physical_account_schema)
        if error:
            return jsonify({"error": RESPONSE_MESSAGES["validation_error"], "message": error}), status.HTTP_400_BAD_REQUEST
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
        return jsonify({"status": "updated"}), status.HTTP_200_OK

    if request.method == 'DELETE':
        safe_db_query(
            'DELETE FROM accounts WHERE id = ? AND type = ?',
            (account_id, ACCOUNT_TYPES["physical"]),
            commit=True
        )
        return '', status.HTTP_204_NO_CONTENT

    return jsonify({"error": RESPONSE_MESSAGES["method_not_allowed"]}), status.HTTP_405_METHOD_NOT_ALLOWED

@accounts_bp.route('/accounts-le-v2.0.0/', methods=['GET', 'POST'])
@swag_from('../docs/accounts.yml')
def legal_accounts():
    logger.info(f"{request.method} {request.path}")
    if request.method == 'GET':
        cur = safe_db_query(
            'SELECT * FROM accounts WHERE type = ?',
            (ACCOUNT_TYPES["legal"],)
        )
        return jsonify([dict(row) for row in cur.fetchall()]), status.HTTP_200_OK

    if request.method == 'POST':
        error = safe_validate(request.json, legal_account_schema)
        if error:
            return jsonify({"error": RESPONSE_MESSAGES["validation_error"], "message": error}), status.HTTP_400_BAD_REQUEST

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
        return jsonify(dict(cur.fetchone())), status.HTTP_201_CREATED

    return jsonify({"error": RESPONSE_MESSAGES["method_not_allowed"]}), status.HTTP_405_METHOD_NOT_ALLOWED

@accounts_bp.route('/accounts-le-v2.0.0/<account_id>', methods=['GET', 'PUT', 'DELETE'])
@swag_from('../docs/accounts.yml')
def legal_account(account_id):
    logger.info(f"{request.method} {request.path} | id={account_id}")
    if request.method == 'GET':
        cur = safe_db_query(
            'SELECT * FROM accounts WHERE id = ? AND type = ?',
            (account_id, ACCOUNT_TYPES["legal"])
        )
        account = cur.fetchone()
        if not account:
            return jsonify({"error": RESPONSE_MESSAGES["not_found"]}), status.HTTP_404_NOT_FOUND
        return jsonify(dict(account)), status.HTTP_200_OK

    if request.method == 'PUT':
        error = safe_validate(request.json, legal_account_schema)
        if error:
            return jsonify({"error": RESPONSE_MESSAGES["validation_error"], "message": error}), status.HTTP_400_BAD_REQUEST
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
        return jsonify({"status": "updated"}), status.HTTP_200_OK

    if request.method == 'DELETE':
        safe_db_query(
            'DELETE FROM accounts WHERE id = ? AND type = ?',
            (account_id, ACCOUNT_TYPES["legal"]),
            commit=True
        )
        return '', status.HTTP_204_NO_CONTENT

    return jsonify({"error": RESPONSE_MESSAGES["method_not_allowed"]}), status.HTTP_405_METHOD_NOT_ALLOWED
