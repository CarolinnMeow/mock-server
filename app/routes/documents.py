from flask import Blueprint, jsonify, request, abort
from jsonschema import validate, ValidationError
from flasgger import swag_from
import uuid
import logging
from app.config import (
    RESPONSE_MESSAGES,
    HTTP_STATUS_CODES,
    HTTP_METHODS,
    DOCUMENT_TYPES
)
from app.db import safe_db_query
from app.utils import log_endpoint, serialize_row

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


def serialize_doc(row):
    return serialize_row(row)


@documents_bp.route('/bank-doc-v1.0.1/', methods=HTTP_METHODS[:2])
@swag_from('../docs/documents.yml')
@log_endpoint
def bank_docs():
    if request.method == 'POST':
        error = safe_validate(request.json, bank_doc_schema)
        if error:
            return jsonify({
                "error": RESPONSE_MESSAGES["validation_error"],
                "message": error
            }), HTTP_STATUS_CODES["BAD_REQUEST"]

        try:
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
            return jsonify(serialize_doc(cur.fetchone())), HTTP_STATUS_CODES["CREATED"]

        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]

    # GET
    try:
        cur = safe_db_query('SELECT * FROM bank_docs')
        return jsonify([serialize_doc(row) for row in cur.fetchall()]), HTTP_STATUS_CODES["OK"]
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]


@documents_bp.route('/bank-doc-v1.0.1/<doc_id>', methods=HTTP_METHODS)
@swag_from('../docs/documents.yml')
@log_endpoint
def bank_doc(doc_id):
    try:
        cur = safe_db_query('SELECT * FROM bank_docs WHERE id = ?', (doc_id,))
        doc = cur.fetchone()

        if not doc:
            return jsonify({"error": RESPONSE_MESSAGES["not_found"]}), HTTP_STATUS_CODES["NOT_FOUND"]

        if request.method == 'PUT':
            error = safe_validate(request.json, bank_doc_schema)
            if error:
                return jsonify({
                    "error": RESPONSE_MESSAGES["validation_error"],
                    "message": error
                }), HTTP_STATUS_CODES["BAD_REQUEST"]

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
            return '', HTTP_STATUS_CODES["NO_CONTENT"]

        return jsonify(serialize_doc(doc)), HTTP_STATUS_CODES["OK"]

    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]


@documents_bp.route('/insurance-doc-v1.0.1/', methods=HTTP_METHODS[:2])
@swag_from('../docs/documents.yml')
@log_endpoint
def insurance_docs():
    if request.method == 'POST':
        error = safe_validate(request.json, insurance_doc_schema)
        if error:
            return jsonify({
                "error": RESPONSE_MESSAGES["validation_error"],
                "message": error
            }), HTTP_STATUS_CODES["BAD_REQUEST"]

        try:
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
            return jsonify(serialize_doc(cur.fetchone())), HTTP_STATUS_CODES["CREATED"]

        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]

    # GET
    try:
        cur = safe_db_query('SELECT * FROM insurance_docs')
        return jsonify([serialize_doc(row) for row in cur.fetchall()]), HTTP_STATUS_CODES["OK"]
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]


@documents_bp.route('/insurance-doc-v1.0.1/<doc_id>', methods=HTTP_METHODS)
@swag_from('../docs/documents.yml')
@log_endpoint
def insurance_doc(doc_id):
    try:
        cur = safe_db_query('SELECT * FROM insurance_docs WHERE id = ?', (doc_id,))
        doc = cur.fetchone()

        if not doc:
            return jsonify({"error": RESPONSE_MESSAGES["not_found"]}), HTTP_STATUS_CODES["NOT_FOUND"]

        if request.method == 'PUT':
            error = safe_validate(request.json, insurance_doc_schema)
            if error:
                return jsonify({
                    "error": RESPONSE_MESSAGES["validation_error"],
                    "message": error
                }), HTTP_STATUS_CODES["BAD_REQUEST"]

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
            return '', HTTP_STATUS_CODES["NO_CONTENT"]

        return jsonify(serialize_doc(doc)), HTTP_STATUS_CODES["OK"]

    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]
