from flask import Blueprint, jsonify, request
from flask_api import status
from jsonschema import ValidationError
from flasgger import swag_from
import uuid
import json
import logging
from app.config import RESPONSE_MESSAGES, AGREEMENT_STATUSES
from app.schemas.product_agreement import product_agreement_schema
from app.db import execute_query

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


def safe_db_query(query, params=(), commit=False):
    try:
        return execute_query(query, params, commit)
    except Exception as e:
        logger.error(f"Agreement DB error: {e}")
        return None


def serialize_agreement(row):
    if not row:
        return {}
    data = dict(row)
    if 'terms' in data:
        try:
            data['terms'] = json.loads(data['terms'])
        except json.JSONDecodeError:
            data['terms'] = []
    return data


@product_agreements_bp.route('/product-agreement-consents-v1.0.1/', methods=['GET', 'POST'])
@swag_from('../docs/product_agreements.yml')
def product_agreements():
    logger.info(f"{request.method} {request.path}")

    if request.method == 'POST':
        error = safe_validate(request.json, product_agreement_schema)
        if error:
            return jsonify({
                "error": RESPONSE_MESSAGES["validation_error"],
                "message": error
            }), status.HTTP_400_BAD_REQUEST

        agreement_id = str(uuid.uuid4())
        terms_str = json.dumps(request.json.get('terms', []))

        result = safe_db_query(
            '''INSERT INTO product_agreements 
               (id, product_type, terms, status)
               VALUES (?, ?, ?, ?)''',
            (
                agreement_id,
                request.json['product_type'],
                terms_str,
                AGREEMENT_STATUSES["active"]
            ),
            commit=True
        )

        if not result:
            return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), status.HTTP_500_INTERNAL_SERVER_ERROR

        cur = safe_db_query('SELECT * FROM product_agreements WHERE id = ?', (agreement_id,))
        return jsonify(serialize_agreement(cur.fetchone())), status.HTTP_201_CREATED

    # GET
    cur = safe_db_query('SELECT * FROM product_agreements')
    agreements = [serialize_agreement(row) for row in cur.fetchall()] if cur else []
    return jsonify(agreements), status.HTTP_200_OK


@product_agreements_bp.route('/product-agreement-consents-v1.0.1/<agreement_id>', methods=['GET', 'PUT', 'DELETE'])
@swag_from('../docs/product_agreements.yml')
def single_product_agreement(agreement_id):
    logger.info(f"{request.method} {request.path} | id={agreement_id}")

    cur = safe_db_query('SELECT * FROM product_agreements WHERE id = ?', (agreement_id,))
    agreement = cur.fetchone() if cur else None

    if not agreement:
        return jsonify({"error": RESPONSE_MESSAGES["not_found"]}), status.HTTP_404_NOT_FOUND

    if request.method == 'PUT':
        error = safe_validate(request.json, product_agreement_schema)
        if error:
            return jsonify({
                "error": RESPONSE_MESSAGES["validation_error"],
                "message": error
            }), status.HTTP_400_BAD_REQUEST

        terms_str = json.dumps(request.json.get('terms', []))
        result = safe_db_query(
            '''UPDATE product_agreements 
               SET product_type = ?, terms = ? 
               WHERE id = ?''',
            (
                request.json['product_type'],
                terms_str,
                agreement_id
            ),
            commit=True
        )

        if not result:
            return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), status.HTTP_500_INTERNAL_SERVER_ERROR

        cur = safe_db_query('SELECT * FROM product_agreements WHERE id = ?', (agreement_id,))
        agreement = cur.fetchone()

    elif request.method == 'DELETE':
        result = safe_db_query(
            'DELETE FROM product_agreements WHERE id = ?',
            (agreement_id,),
            commit=True
        )
        if not result:
            return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), status.HTTP_500_INTERNAL_SERVER_ERROR
        return '', status.HTTP_204_NO_CONTENT

    return jsonify(serialize_agreement(agreement)), status.HTTP_200_OK
