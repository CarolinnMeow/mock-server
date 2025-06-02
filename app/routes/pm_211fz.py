from flask import Blueprint, jsonify, request
from jsonschema import validate, ValidationError
from flasgger import swag_from
import uuid
import logging
from app.schemas.pm_211fz import pm_211fz_schema
from app.config import (
    RESPONSE_MESSAGES,
    PAYMENT_STATUSES,
    PAYMENT_TYPES,
    HTTP_STATUS_CODES,
    HTTP_METHODS
)
from app.db import safe_db_query
from app.utils import log_endpoint, serialize_row

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pm_211fz_bp = Blueprint('pm_211fz', __name__)


def safe_validate(data, schema):
    try:
        validate(data, schema)
        return None
    except ValidationError as e:
        logger.warning(f"PM 211-FZ validation error: {e}")
        return str(e)


@pm_211fz_bp.route('/pm-211fz-v1.3.1/', methods=HTTP_METHODS[:2])
@swag_from('../docs/pm_211fz.yml')
@log_endpoint
def pm_211fz_operations():
    if request.method == 'POST':
        return handle_pm_211fz_creation(request.json)

    return handle_pm_211fz_list()


def handle_pm_211fz_creation(data):
    error = safe_validate(data, pm_211fz_schema)
    if error:
        return jsonify({
            "error": RESPONSE_MESSAGES["validation_error"],
            "message": error
        }), HTTP_STATUS_CODES["BAD_REQUEST"]

    try:
        payment_id = str(uuid.uuid4())
        safe_db_query(
            '''INSERT INTO payments 
            (id, status, type, amount, currency, recipient, purpose, budget_code, created_at, account_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)''',
            (
                payment_id,
                PAYMENT_STATUSES["pending"],
                PAYMENT_TYPES["pm_211fz"],
                data['amount'],
                data['currency'],
                data['recipient'],
                data['purpose'],
                data['budget_code'],
                data['account_id']
            ),
            commit=True
        )
        cur = safe_db_query('SELECT * FROM payments WHERE id = ?', (payment_id,))
        return jsonify(serialize_row(cur.fetchone())), HTTP_STATUS_CODES["CREATED"]

    except Exception as e:
        logger.error(f"Payment creation failed: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]


def handle_pm_211fz_list():
    try:
        cur = safe_db_query('SELECT * FROM payments WHERE type = ?', (PAYMENT_TYPES["pm_211fz"],))
        payments = [serialize_row(row) for row in cur.fetchall()] if cur else []
        return jsonify(payments), HTTP_STATUS_CODES["OK"]

    except Exception as e:
        logger.error(f"Payment list retrieval failed: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]


@pm_211fz_bp.route('/pm-211fz-v1.3.1/<payment_id>', methods=HTTP_METHODS)
@swag_from('../docs/pm_211fz.yml')
@log_endpoint
def single_pm_211fz(payment_id):
    try:
        payment = get_payment(payment_id)

        if not payment:
            return jsonify({"error": RESPONSE_MESSAGES["not_found"]}), HTTP_STATUS_CODES["NOT_FOUND"]

        if request.method == 'PUT':
            return update_pm_211fz(payment_id, request.json)

        if request.method == 'DELETE':
            return delete_pm_211fz(payment_id)

        return jsonify(serialize_row(payment)), HTTP_STATUS_CODES["OK"]

    except Exception as e:
        logger.error(f"Payment operation failed: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["server_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]


def get_payment(payment_id):
    cur = safe_db_query(
        'SELECT * FROM payments WHERE id = ? AND type = ?',
        (payment_id, PAYMENT_TYPES["pm_211fz"])
    )
    return cur.fetchone() if cur else None


def update_pm_211fz(payment_id, data):
    error = safe_validate(data, pm_211fz_schema)
    if error:
        return jsonify({
            "error": RESPONSE_MESSAGES["validation_error"],
            "message": error
        }), HTTP_STATUS_CODES["BAD_REQUEST"]

    try:
        safe_db_query(
            '''UPDATE payments SET 
            amount = ?, currency = ?, recipient = ? 
            WHERE id = ? AND type = ?''',
            (
                data['amount'],
                data['currency'],
                data['recipient'],
                payment_id,
                PAYMENT_TYPES["pm_211fz"]
            ),
            commit=True
        )
        cur = safe_db_query('SELECT * FROM payments WHERE id = ?', (payment_id,))
        return jsonify(serialize_row(cur.fetchone())), HTTP_STATUS_CODES["OK"]

    except Exception as e:
        logger.error(f"Payment update failed: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]


def delete_pm_211fz(payment_id):
    try:
        safe_db_query(
            'DELETE FROM payments WHERE id = ? AND type = ?',
            (payment_id, PAYMENT_TYPES["pm_211fz"]),
            commit=True
        )
        return '', HTTP_STATUS_CODES["NO_CONTENT"]

    except Exception as e:
        logger.error(f"Payment deletion failed: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]
