from flask import Blueprint, jsonify, request, abort
from jsonschema import validate, ValidationError
from flasgger import swag_from
import uuid
import json
import logging
from app.config import (
    CONSENT_TYPES,
    RESPONSE_MESSAGES,
    HTTP_STATUS_CODES,
    HTTP_METHODS
)
from app.db import execute_query, safe_db_query
from app.utils import log_endpoint, serialize_row

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

consents_bp = Blueprint('consents', __name__)


def safe_validate(data, schema):
    try:
        validate(data, schema)
        return None
    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return str(e)


def serialize_consent(row):
    result = serialize_row(row)
    if 'permissions' in result:
        try:
            result['permissions'] = json.loads(result['permissions'])
        except (json.JSONDecodeError, TypeError):
            result['permissions'] = []
    return result


@consents_bp.route('/consent-pe-v2.0.0/', methods=[HTTP_METHODS[1]])  # POST
@swag_from('../docs/consents.yml')
@log_endpoint
def create_pe_consent():
    error = safe_validate(request.json, consent_schema)
    if error:
        return jsonify({
            "error": RESPONSE_MESSAGES["validation_error"],
            "message": error
        }), HTTP_STATUS_CODES["BAD_REQUEST"]

    consent_id = str(uuid.uuid4())
    try:
        safe_db_query(
            '''INSERT INTO consents 
            (id, type, status, tpp_id, permissions) 
            VALUES (?, ?, ?, ?, ?)''',
            (
                consent_id,
                CONSENT_TYPES["physical"],
                "ACTIVE",
                request.json.get('tpp_id'),
                json.dumps(request.json.get('permissions', []))
            ),
            commit=True
        )
    except Exception as e:
        logger.error(f"DB error: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]

    cur = safe_db_query('SELECT * FROM consents WHERE id = ?', (consent_id,))
    return jsonify(serialize_consent(cur.fetchone())), HTTP_STATUS_CODES["CREATED"]


@consents_bp.route('/consent-le-v2.0.0/', methods=[HTTP_METHODS[1]])  # POST
@swag_from('../docs/consents.yml')
@log_endpoint
def create_le_consent():
    error = safe_validate(request.json, consent_schema)
    if error:
        return jsonify({
            "error": RESPONSE_MESSAGES["validation_error"],
            "message": error
        }), HTTP_STATUS_CODES["BAD_REQUEST"]

    consent_id = str(uuid.uuid4())
    try:
        safe_db_query(
            '''INSERT INTO consents 
            (id, type, status, tpp_id, permissions) 
            VALUES (?, ?, ?, ?, ?)''',
            (
                consent_id,
                CONSENT_TYPES["legal"],
                "ACTIVE",
                request.json.get('tpp_id'),
                json.dumps(request.json.get('permissions', []))
            ),
            commit=True
        )
    except Exception as e:
        logger.error(f"DB error: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]

    cur = safe_db_query('SELECT * FROM consents WHERE id = ?', (consent_id,))
    return jsonify(serialize_consent(cur.fetchone())), HTTP_STATUS_CODES["CREATED"]


@consents_bp.route('/consent-pe-v2.0.0/<consent_id>', methods=HTTP_METHODS)
@swag_from('../docs/consents.yml')
@log_endpoint
def pe_consent(consent_id):
    cur = safe_db_query(
        'SELECT * FROM consents WHERE id = ? AND type = ?',
        (consent_id, CONSENT_TYPES["physical"])
    )
    consent = cur.fetchone() if cur else None

    if not consent:
        return jsonify({"error": RESPONSE_MESSAGES["not_found"]}), HTTP_STATUS_CODES["NOT_FOUND"]

    if request.method == 'PUT':
        error = safe_validate(request.json, consent_schema)
        if error:
            return jsonify({
                "error": RESPONSE_MESSAGES["validation_error"],
                "message": error
            }), HTTP_STATUS_CODES["BAD_REQUEST"]

        update_fields = []
        params = []
        for field in ['status', 'tpp_id', 'permissions']:
            if field in request.json:
                update_fields.append(f"{field} = ?")
                params.append(
                    json.dumps(request.json[field]) if field == 'permissions'
                    else request.json[field]
                )

        if update_fields:
            params.extend([consent_id, CONSENT_TYPES["physical"]])
            safe_db_query(
                f"UPDATE consents SET {', '.join(update_fields)} WHERE id = ? AND type = ?",
                params,
                commit=True
            )

        cur = safe_db_query(
            'SELECT * FROM consents WHERE id = ? AND type = ?',
            (consent_id, CONSENT_TYPES["physical"])
        )
        consent = cur.fetchone()

    elif request.method == 'DELETE':
        safe_db_query(
            'DELETE FROM consents WHERE id = ? AND type = ?',
            (consent_id, CONSENT_TYPES["physical"]),
            commit=True
        )
        return '', HTTP_STATUS_CODES["NO_CONTENT"]

    return jsonify(serialize_consent(consent)), HTTP_STATUS_CODES["OK"]


@consents_bp.route('/consent-le-v2.0.0/<consent_id>', methods=HTTP_METHODS)
@swag_from('../docs/consents.yml')
@log_endpoint
def le_consent(consent_id):
    cur = safe_db_query(
        'SELECT * FROM consents WHERE id = ? AND type = ?',
        (consent_id, CONSENT_TYPES["legal"])
    )
    consent = cur.fetchone() if cur else None

    if not consent:
        return jsonify({"error": RESPONSE_MESSAGES["not_found"]}), HTTP_STATUS_CODES["NOT_FOUND"]

    if request.method == 'PUT':
        error = safe_validate(request.json, consent_schema)
        if error:
            return jsonify({
                "error": RESPONSE_MESSAGES["validation_error"],
                "message": error
            }), HTTP_STATUS_CODES["BAD_REQUEST"]

        update_fields = []
        params = []
        for field in ['status', 'tpp_id', 'permissions']:
            if field in request.json:
                update_fields.append(f"{field} = ?")
                params.append(
                    json.dumps(request.json[field]) if field == 'permissions'
                    else request.json[field]
                )

        if update_fields:
            params.extend([consent_id, CONSENT_TYPES["legal"]])
            safe_db_query(
                f"UPDATE consents SET {', '.join(update_fields)} WHERE id = ? AND type = ?",
                params,
                commit=True
            )

        cur = safe_db_query(
            'SELECT * FROM consents WHERE id = ? AND type = ?',
            (consent_id, CONSENT_TYPES["legal"])
        )
        consent = cur.fetchone()

    elif request.method == 'DELETE':
        safe_db_query(
            'DELETE FROM consents WHERE id = ? AND type = ?',
            (consent_id, CONSENT_TYPES["legal"]),
            commit=True
        )
        return '', HTTP_STATUS_CODES["NO_CONTENT"]

    return jsonify(serialize_consent(consent)), HTTP_STATUS_CODES["OK"]
