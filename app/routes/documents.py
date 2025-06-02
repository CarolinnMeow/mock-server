from flask import Blueprint, jsonify, request, abort
from flask_api import status
from jsonschema import validate, ValidationError
from flasgger import swag_from
from app.db import execute_query
import uuid
import logging
from app.config import RESPONSE_MESSAGES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

documents_bp = Blueprint('documents', __name__)


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


def serialize_doc(row):
    return dict(row)


@documents_bp.route('/bank-doc-v1.0.1/', methods=['GET', 'POST'])
@swag_from('../docs/documents.yml')
def bank_docs():
    logger.info(f"{request.method} {request.path}")

    if request.method == 'POST':
        error = safe_validate(request.json, bank_doc_schema)
        if error:
            return jsonify(
                {"error": RESPONSE_MESSAGES["validation_error"], "message": error}), status.HTTP_400_BAD_REQUEST

        doc_id = str(uuid.uuid4())
        safe_db_query(
            '''INSERT INTO bank_docs 
               (id, type, content, signature, created_at, account_id)
               VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)''',
            (
                doc_id,
                request.json['type'],
                request.json['content'],
                request.json['signature'],
                request.json['account_id']
            ),
            commit=True
        )
        cur = safe_db_query('SELECT * FROM bank_docs WHERE id = ?', (doc_id,))
        return jsonify(serialize_doc(cur.fetchone())), status.HTTP_201_CREATED

    # GET
    cur = safe_db_query('SELECT * FROM bank_docs')
    return jsonify([serialize_doc(row) for row in cur.fetchall()]), status.HTTP_200_OK


@documents_bp.route('/bank-doc-v1.0.1/<doc_id>', methods=['GET', 'PUT', 'DELETE'])
@swag_from('../docs/documents.yml')
def bank_doc(doc_id):
    logger.info(f"{request.method} {request.path} | id={doc_id}")

    cur = safe_db_query('SELECT * FROM bank_docs WHERE id = ?', (doc_id,))
    doc = cur.fetchone()
    if not doc:
        return jsonify({"error": RESPONSE_MESSAGES["not_found"]}), status.HTTP_404_NOT_FOUND

    if request.method == 'PUT':
        error = safe_validate(request.json, bank_doc_schema)
        if error:
            return jsonify(
                {"error": RESPONSE_MESSAGES["validation_error"], "message": error}), status.HTTP_400_BAD_REQUEST

        safe_db_query(
            '''UPDATE bank_docs SET 
               type = ?, content = ?, signature = ? 
               WHERE id = ?''',
            (
                request.json['type'],
                request.json['content'],
                request.json['signature'],
                doc_id
            ),
            commit=True
        )
        cur = safe_db_query('SELECT * FROM bank_docs WHERE id = ?', (doc_id,))
        doc = cur.fetchone()

    elif request.method == 'DELETE':
        safe_db_query('DELETE FROM bank_docs WHERE id = ?', (doc_id,), commit=True)
        return '', status.HTTP_204_NO_CONTENT

    return jsonify(serialize_doc(doc)), status.HTTP_200_OK


@documents_bp.route('/insurance-doc-v1.0.1/', methods=['GET', 'POST'])
@swag_from('../docs/documents.yml')
def insurance_docs():
    logger.info(f"{request.method} {request.path}")

    if request.method == 'POST':
        error = safe_validate(request.json, insurance_doc_schema)
        if error:
            return jsonify(
                {"error": RESPONSE_MESSAGES["validation_error"], "message": error}), status.HTTP_400_BAD_REQUEST

        doc_id = str(uuid.uuid4())
        safe_db_query(
            '''INSERT INTO insurance_docs 
               (id, type, content, policy_number, valid_until, created_at)
               VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)''',
            (
                doc_id,
                request.json['type'],
                request.json['content'],
                request.json['policy_number'],
                request.json['valid_until']
            ),
            commit=True
        )
        cur = safe_db_query('SELECT * FROM insurance_docs WHERE id = ?', (doc_id,))
        return jsonify(serialize_doc(cur.fetchone())), status.HTTP_201_CREATED

    # GET
    cur = safe_db_query('SELECT * FROM insurance_docs')
    return jsonify([serialize_doc(row) for row in cur.fetchall()]), status.HTTP_200_OK


@documents_bp.route('/insurance-doc-v1.0.1/<doc_id>', methods=['GET', 'PUT', 'DELETE'])
@swag_from('../docs/documents.yml')
def insurance_doc(doc_id):
    logger.info(f"{request.method} {request.path} | id={doc_id}")

    cur = safe_db_query('SELECT * FROM insurance_docs WHERE id = ?', (doc_id,))
    doc = cur.fetchone()
    if not doc:
        return jsonify({"error": RESPONSE_MESSAGES["not_found"]}), status.HTTP_404_NOT_FOUND

    if request.method == 'PUT':
        error = safe_validate(request.json, insurance_doc_schema)
        if error:
            return jsonify(
                {"error": RESPONSE_MESSAGES["validation_error"], "message": error}), status.HTTP_400_BAD_REQUEST

        safe_db_query(
            '''UPDATE insurance_docs SET 
               type = ?, content = ?, policy_number = ?, valid_until = ? 
               WHERE id = ?''',
            (
                request.json['type'],
                request.json['content'],
                request.json['policy_number'],
                request.json['valid_until'],
                doc_id
            ),
            commit=True
        )
        cur = safe_db_query('SELECT * FROM insurance_docs WHERE id = ?', (doc_id,))
        doc = cur.fetchone()

    elif request.method == 'DELETE':
        safe_db_query('DELETE FROM insurance_docs WHERE id = ?', (doc_id,), commit=True)
        return '', status.HTTP_204_NO_CONTENT

    return jsonify(serialize_doc(doc)), status.HTTP_200_OK
