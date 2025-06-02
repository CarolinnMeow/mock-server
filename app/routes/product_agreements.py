from flask import Blueprint, jsonify, request
from jsonschema import validate, ValidationError
from flasgger import swag_from
import uuid
import json
import logging
from app.schemas.product_agreement import product_agreement_schema
from app.config import (
    RESPONSE_MESSAGES,
    AGREEMENT_STATUSES,
    HTTP_STATUS_CODES,
    HTTP_METHODS
)
from app.db import safe_db_query
from app.utils import log_endpoint, serialize_row

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

product_agreements_bp = Blueprint('product_agreements', __name__)


def safe_validate(data, schema):
    try:
        validate(data, schema)
        return None
    except ValidationError as e:
        logger.warning(f"Agreement validation error: {e}")
        return str(e)


def serialize_agreement(row):
    data = serialize_row(row)
    if 'terms' in data:
        try:
            data['terms'] = json.loads(data['terms'])
        except (json.JSONDecodeError, TypeError):
            data['terms'] = []
    return data


@product_agreements_bp.route('/product-agreement-consents-v1.0.1/', methods=HTTP_METHODS[:2])
@swag_from('../docs/product_agreements.yml')
@log_endpoint
def product_agreements():
    if request.method == 'POST':
        return handle_agreement_creation(request.json)

    return handle_agreements_list()


def handle_agreement_creation(data):
    error = safe_validate(data, product_agreement_schema)
    if error:
        return jsonify({
            "error": RESPONSE_MESSAGES["validation_error"],
            "message": error
        }), HTTP_STATUS_CODES["BAD_REQUEST"]

    try:
        agreement_id = str(uuid.uuid4())
        terms_str = json.dumps(data.get('terms', []))

        safe_db_query(
            '''INSERT INTO product_agreements 
            (id, product_type, terms, status)
            VALUES (?, ?, ?, ?)''',
            (
                agreement_id,
                data['product_type'],
                terms_str,
                AGREEMENT_STATUSES["active"]
            ),
            commit=True
        )

        cur = safe_db_query('SELECT * FROM product_agreements WHERE id = ?', (agreement_id,))
        return jsonify(serialize_agreement(cur.fetchone())), HTTP_STATUS_CODES["CREATED"]

    except Exception as e:
        logger.error(f"Agreement creation failed: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]


def handle_agreements_list():
    try:
        cur = safe_db_query('SELECT * FROM product_agreements')
        agreements = [serialize_agreement(row) for row in cur.fetchall()] if cur else []
        return jsonify(agreements), HTTP_STATUS_CODES["OK"]

    except Exception as e:
        logger.error(f"Agreements list retrieval failed: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]


@product_agreements_bp.route('/product-agreement-consents-v1.0.1/<agreement_id>', methods=HTTP_METHODS)
@swag_from('../docs/product_agreements.yml')
@log_endpoint
def single_product_agreement(agreement_id):
    try:
        agreement = get_agreement(agreement_id)

        if not agreement:
            return jsonify({"error": RESPONSE_MESSAGES["not_found"]}), HTTP_STATUS_CODES["NOT_FOUND"]

        if request.method == 'PUT':
            return update_agreement(agreement_id, request.json)

        if request.method == 'DELETE':
            return delete_agreement(agreement_id)

        return jsonify(serialize_agreement(agreement)), HTTP_STATUS_CODES["OK"]

    except Exception as e:
        logger.error(f"Agreement operation failed: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["server_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]


def get_agreement(agreement_id):
    cur = safe_db_query('SELECT * FROM product_agreements WHERE id = ?', (agreement_id,))
    return cur.fetchone() if cur else None


def update_agreement(agreement_id, data):
    error = safe_validate(data, product_agreement_schema)
    if error:
        return jsonify({
            "error": RESPONSE_MESSAGES["validation_error"],
            "message": error
        }), HTTP_STATUS_CODES["BAD_REQUEST"]

    try:
        terms_str = json.dumps(data.get('terms', []))
        safe_db_query(
            '''UPDATE product_agreements 
            SET product_type = ?, terms = ? 
            WHERE id = ?''',
            (
                data['product_type'],
                terms_str,
                agreement_id
            ),
            commit=True
        )
        cur = safe_db_query('SELECT * FROM product_agreements WHERE id = ?', (agreement_id,))
        return jsonify(serialize_agreement(cur.fetchone())), HTTP_STATUS_CODES["OK"]

    except Exception as e:
        logger.error(f"Agreement update failed: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]


def delete_agreement(agreement_id):
    try:
        safe_db_query(
            'DELETE FROM product_agreements WHERE id = ?',
            (agreement_id,),
            commit=True
        )
        return '', HTTP_STATUS_CODES["NO_CONTENT"]

    except Exception as e:
        logger.error(f"Agreement deletion failed: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]
