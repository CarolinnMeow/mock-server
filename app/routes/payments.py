from flask import Blueprint, jsonify, request
from flask_api import status
from jsonschema import ValidationError
from flasgger import swag_from
import uuid
from datetime import datetime
import logging
from app.config import RESPONSE_MESSAGES, PAYMENT_STATUSES
from app.schemas.payment import payment_schema
from app.db import execute_query

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


def safe_db_query(query, params=(), commit=False):
    try:
        return execute_query(query, params, commit)
    except Exception as e:
        logger.error(f"Payment DB error: {e}")
        return None


def serialize_payment(row):
    return dict(row) if row else {}


@payments_bp.route('/payments-v1.3.1/', methods=['POST'])
@swag_from('../docs/payments.yml')
def create_payment():
    logger.info(f"POST {request.path}")

    error = safe_validate(request.json, payment_schema)
    if error:
        return jsonify({
            "error": RESPONSE_MESSAGES["validation_error"],
            "message": error
        }), status.HTTP_400_BAD_REQUEST

    payment_id = str(uuid.uuid4())
    result = safe_db_query(
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

    if not result:
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), status.HTTP_500_INTERNAL_SERVER_ERROR

    cur = safe_db_query('SELECT * FROM payments WHERE id = ?', (payment_id,))
    return jsonify(serialize_payment(cur.fetchone())), status.HTTP_201_CREATED


@payments_bp.route('/payments-v1.3.1/<payment_id>', methods=['GET', 'PUT', 'DELETE'])
@swag_from('../docs/payments.yml')
def payment_operations(payment_id):
    logger.info(f"{request.method} {request.path} | id={payment_id}")

    cur = safe_db_query('SELECT * FROM payments WHERE id = ?', (payment_id,))
    payment = cur.fetchone() if cur else None

    if not payment:
        return jsonify({"error": RESPONSE_MESSAGES["not_found"]}), status.HTTP_404_NOT_FOUND

    if request.method == 'PUT':
        error = safe_validate(request.json, payment_schema)
        if error:
            return jsonify({
                "error": RESPONSE_MESSAGES["validation_error"],
                "message": error
            }), status.HTTP_400_BAD_REQUEST

        result = safe_db_query(
            '''UPDATE payments 
               SET amount = ?, currency = ?, recipient = ? 
               WHERE id = ?''',
            (
                request.json['amount'],
                request.json['currency'],
                request.json['recipient'],
                payment_id
            ),
            commit=True
        )

        if not result:
            return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), status.HTTP_500_INTERNAL_SERVER_ERROR

        cur = safe_db_query('SELECT * FROM payments WHERE id = ?', (payment_id,))
        payment = cur.fetchone()

    elif request.method == 'DELETE':
        result = safe_db_query('DELETE FROM payments WHERE id = ?', (payment_id,), commit=True)
        if not result:
            return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), status.HTTP_500_INTERNAL_SERVER_ERROR
        return '', status.HTTP_204_NO_CONTENT

    return jsonify(serialize_payment(payment)), status.HTTP_200_OK
