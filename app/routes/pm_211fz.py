from flask import Blueprint, jsonify, request
from flask_api import status
from jsonschema import ValidationError
from flasgger import swag_from
import uuid
import logging
from app.config import RESPONSE_MESSAGES, PAYMENT_STATUSES, PAYMENT_TYPES
from app.schemas.pm_211fz import pm_211fz_schema
from app.db import execute_query

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


def safe_db_query(query, params=(), commit=False):
    try:
        return execute_query(query, params, commit)
    except Exception as e:
        logger.error(f"PM 211-FZ DB error: {e}")
        return None


def serialize_payment(row):
    return dict(row) if row else {}


@pm_211fz_bp.route('/pm-211fz-v1.3.1/', methods=['GET', 'POST'])
@swag_from('../docs/pm_211fz.yml')
def pm_211fz():
    logger.info(f"{request.method} {request.path}")

    if request.method == 'POST':
        error = safe_validate(request.json, pm_211fz_schema)
        if error:
            return jsonify({
                "error": RESPONSE_MESSAGES["validation_error"],
                "message": error
            }), status.HTTP_400_BAD_REQUEST

        payment_id = str(uuid.uuid4())
        result = safe_db_query(
            '''INSERT INTO payments 
            (id, status, type, amount, currency, recipient, purpose, budget_code, created_at, account_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)''',
            (
                payment_id,
                PAYMENT_STATUSES["pending"],
                PAYMENT_TYPES["pm_211fz"],
                request.json['amount'],
                request.json['currency'],
                request.json['recipient'],
                request.json['purpose'],
                request.json['budget_code'],
                request.json['account_id']
            ),
            commit=True
        )

        if not result:
            return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), status.HTTP_500_INTERNAL_SERVER_ERROR

        cur = safe_db_query('SELECT * FROM payments WHERE id = ?', (payment_id,))
        return jsonify(serialize_payment(cur.fetchone())), status.HTTP_201_CREATED

    # GET
    cur = safe_db_query('SELECT * FROM payments WHERE type = ?', (PAYMENT_TYPES["pm_211fz"],))
    payments = [serialize_payment(row) for row in cur.fetchall()] if cur else []
    return jsonify(payments), status.HTTP_200_OK


@pm_211fz_bp.route('/pm-211fz-v1.3.1/<payment_id>', methods=['GET', 'PUT', 'DELETE'])
@swag_from('../docs/pm_211fz.yml')
def single_pm_211fz(payment_id):
    logger.info(f"{request.method} {request.path} | id={payment_id}")

    cur = safe_db_query(
        'SELECT * FROM payments WHERE id = ? AND type = ?',
        (payment_id, PAYMENT_TYPES["pm_211fz"])
    )
    payment = cur.fetchone() if cur else None

    if not payment:
        return jsonify({"error": RESPONSE_MESSAGES["not_found"]}), status.HTTP_404_NOT_FOUND

    if request.method == 'PUT':
        error = safe_validate(request.json, pm_211fz_schema)
        if error:
            return jsonify({
                "error": RESPONSE_MESSAGES["validation_error"],
                "message": error
            }), status.HTTP_400_BAD_REQUEST

        result = safe_db_query(
            '''UPDATE payments SET 
            amount = ?, currency = ?, recipient = ? 
            WHERE id = ? AND type = ?''',
            (
                request.json['amount'],
                request.json['currency'],
                request.json['recipient'],
                payment_id,
                PAYMENT_TYPES["pm_211fz"]
            ),
            commit=True
        )

        if not result:
            return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), status.HTTP_500_INTERNAL_SERVER_ERROR

        cur = safe_db_query('SELECT * FROM payments WHERE id = ?', (payment_id,))
        payment = cur.fetchone()

    elif request.method == 'DELETE':
        result = safe_db_query(
            'DELETE FROM payments WHERE id = ? AND type = ?',
            (payment_id, PAYMENT_TYPES["pm_211fz"]),
            commit=True
        )
        if not result:
            return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), status.HTTP_500_INTERNAL_SERVER_ERROR
        return '', status.HTTP_204_NO_CONTENT

    return jsonify(serialize_payment(payment)), status.HTTP_200_OK
