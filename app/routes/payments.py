from flask import Blueprint, jsonify, request
from jsonschema import validate, ValidationError
from flasgger import swag_from
import uuid
from datetime import datetime
import logging
from app.schemas.payment import payment_schema
from app.config import (
    RESPONSE_MESSAGES,
    PAYMENT_STATUSES,
    HTTP_STATUS_CODES,
    HTTP_METHODS
)
from app.db import safe_db_query
from app.utils import log_endpoint, serialize_row

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

payments_bp = Blueprint('payments', __name__)


def safe_validate(data, schema):
    try:
        validate(data, schema)
        return None
    except ValidationError as e:
        logger.warning(f"Payment validation error: {e}")
        return str(e)


@payments_bp.route('/payments-v1.3.1/', methods=[HTTP_METHODS[1]])  # POST
@swag_from('../docs/payments.yml')
@log_endpoint
def create_payment():
    error = safe_validate(request.json, payment_schema)
    if error:
        return jsonify({
            "error": RESPONSE_MESSAGES["validation_error"],
            "message": error
        }), HTTP_STATUS_CODES["BAD_REQUEST"]

    try:
        payment_id = str(uuid.uuid4())
        safe_db_query(
            '''INSERT INTO payments 
            (id, status, created_at, amount, currency, recipient, account_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (
                payment_id,
                PAYMENT_STATUSES["pending"],
                datetime.now().isoformat(),
                request.json['amount'],
                request.json['currency'],
                request.json['recipient'],
                request.json['account_id']
            ),
            commit=True
        )
        cur = safe_db_query('SELECT * FROM payments WHERE id = ?', (payment_id,))
        return jsonify(serialize_row(cur.fetchone())), HTTP_STATUS_CODES["CREATED"]

    except Exception as e:
        logger.error(f"Payment creation error: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]


@payments_bp.route('/payments-v1.3.1/<payment_id>', methods=HTTP_METHODS)
@swag_from('../docs/payments.yml')
@log_endpoint
def payment_operations(payment_id):
    try:
        cur = safe_db_query('SELECT * FROM payments WHERE id = ?', (payment_id,))
        payment = cur.fetchone() if cur else None

        if not payment:
            return jsonify({"error": RESPONSE_MESSAGES["not_found"]}), HTTP_STATUS_CODES["NOT_FOUND"]

        if request.method == 'PUT':
            return handle_payment_update(payment_id, request.json)

        elif request.method == 'DELETE':
            return handle_payment_deletion(payment_id)

        return jsonify(serialize_row(payment)), HTTP_STATUS_CODES["OK"]

    except Exception as e:
        logger.error(f"Payment operation error: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["server_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]


def handle_payment_update(payment_id, data):
    error = safe_validate(data, payment_schema)
    if error:
        return jsonify({
            "error": RESPONSE_MESSAGES["validation_error"],
            "message": error
        }), HTTP_STATUS_CODES["BAD_REQUEST"]

    try:
        safe_db_query(
            '''UPDATE payments 
            SET amount = ?, currency = ?, recipient = ? 
            WHERE id = ?''',
            (
                data['amount'],
                data['currency'],
                data['recipient'],
                payment_id
            ),
            commit=True
        )
        cur = safe_db_query('SELECT * FROM payments WHERE id = ?', (payment_id,))
        return jsonify(serialize_row(cur.fetchone())), HTTP_STATUS_CODES["OK"]

    except Exception as e:
        logger.error(f"Payment update error: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]


def handle_payment_deletion(payment_id):
    try:
        safe_db_query('DELETE FROM payments WHERE id = ?', (payment_id,), commit=True)
        return '', HTTP_STATUS_CODES["NO_CONTENT"]

    except Exception as e:
        logger.error(f"Payment deletion error: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]
