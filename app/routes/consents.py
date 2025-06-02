from flask import Blueprint, jsonify, request, abort
from flask_api import status
from app.schemas.consent import consent_schema
from jsonschema import validate, ValidationError
from flasgger import swag_from
from app.db import execute_query
import uuid
import json
import logging
from app.config import CONSENT_TYPES, RESPONSE_MESSAGES

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

def safe_db_query(query, params=(), commit=False):
    try:
        return execute_query(query, params, commit)
    except Exception as e:
        logger.error(f"DB error: {e}")
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR, description="Database error")

def serialize_consent(row):
    result = dict(row)
    result['permissions'] = json.loads(result['permissions']) if result.get('permissions') else []
    return result

@swag_from('../docs/consents.yml')
@consents_bp.route('/consent-pe-v2.0.0/', methods=['POST'])
def create_pe_consent():
    logger.info(f"POST {request.path}")
    error = safe_validate(request.json, consent_schema)
    if error:
        return jsonify({"error": RESPONSE_MESSAGES["validation_error"], "message": error}), status.HTTP_400_BAD_REQUEST

    consent_id = str(uuid.uuid4())
    consent = {
        "id": consent_id,
        "type": CONSENT_TYPES["physical"],
        "status": "ACTIVE",
        **request.json
    }
    safe_db_query(
        '''INSERT INTO consents (id, type, status, tpp_id, permissions) VALUES (?, ?, ?, ?, ?)''',
        (
            consent_id,
            CONSENT_TYPES["physical"],
            "ACTIVE",
            consent.get('tpp_id'),
            json.dumps(consent.get('permissions', []))
        ),
        commit=True
    )
    return jsonify(consent), status.HTTP_201_CREATED

@consents_bp.route('/consent-le-v2.0.0/', methods=['POST'])
@swag_from('../docs/consents.yml')
def create_le_consent():
    logger.info(f"POST {request.path}")
    error = safe_validate(request.json, consent_schema)
    if error:
        return jsonify({"error": RESPONSE_MESSAGES["validation_error"], "message": error}), status.HTTP_400_BAD_REQUEST

    consent_id = str(uuid.uuid4())
    consent = {
        "id": consent_id,
        "type": CONSENT_TYPES["legal"],
        "status": "ACTIVE",
        **request.json
    }
    safe_db_query(
        '''INSERT INTO consents (id, type, status, tpp_id, permissions) VALUES (?, ?, ?, ?, ?)''',
        (
            consent_id,
            CONSENT_TYPES["legal"],
            "ACTIVE",
            consent.get('tpp_id'),
            json.dumps(consent.get('permissions', []))
        ),
        commit=True
    )
    return jsonify(consent), status.HTTP_201_CREATED

@consents_bp.route('/consent-pe-v2.0.0/<consent_id>', methods=['GET', 'PUT', 'DELETE'])
@swag_from('../docs/consents.yml')
def pe_consent(consent_id):
    logger.info(f"{request.method} {request.path} | id={consent_id}")
    cur = safe_db_query(
        'SELECT * FROM consents WHERE id = ? AND type = ?', (consent_id, CONSENT_TYPES["physical"])
    )
    consent = cur.fetchone()
    if not consent:
        return jsonify({"error": RESPONSE_MESSAGES["not_found"]}), status.HTTP_404_NOT_FOUND

    if request.method == 'PUT':
        error = safe_validate(request.json, consent_schema)
        if error:
            return jsonify({"error": RESPONSE_MESSAGES["validation_error"], "message": error}), status.HTTP_400_BAD_REQUEST

        fields = []
        values = []
        for key in ['status', 'tpp_id', 'permissions']:
            if key in request.json:
                fields.append(f"{key} = ?")
                val = request.json[key]
                if key == 'permissions':
                    val = json.dumps(val)
                values.append(val)
        if fields:
            values.extend([consent_id, CONSENT_TYPES["physical"]])
            safe_db_query(
                f"UPDATE consents SET {', '.join(fields)} WHERE id = ? AND type = ?",
                values,
                commit=True
            )
        cur = safe_db_query(
            'SELECT * FROM consents WHERE id = ? AND type = ?', (consent_id, CONSENT_TYPES["physical"])
        )
        consent = cur.fetchone()
    elif request.method == 'DELETE':
        safe_db_query(
            'DELETE FROM consents WHERE id = ? AND type = ?', (consent_id, CONSENT_TYPES["physical"]), commit=True
        )
        return '', status.HTTP_204_NO_CONTENT

    return jsonify(serialize_consent(consent)), status.HTTP_200_OK

@consents_bp.route('/consent-le-v2.0.0/<consent_id>', methods=['GET', 'PUT', 'DELETE'])
@swag_from('../docs/consents.yml')
def le_consent(consent_id):
    logger.info(f"{request.method} {request.path} | id={consent_id}")
    cur = safe_db_query(
        'SELECT * FROM consents WHERE id = ? AND type = ?', (consent_id, CONSENT_TYPES["legal"])
    )
    consent = cur.fetchone()
    if not consent:
        return jsonify({"error": RESPONSE_MESSAGES["not_found"]}), status.HTTP_404_NOT_FOUND

    if request.method == 'PUT':
        error = safe_validate(request.json, consent_schema)
        if error:
            return jsonify({"error": RESPONSE_MESSAGES["validation_error"], "message": error}), status.HTTP_400_BAD_REQUEST

        fields = []
        values = []
        for key in ['status', 'tpp_id', 'permissions']:
            if key in request.json:
                fields.append(f"{key} = ?")
                val = request.json[key]
                if key == 'permissions':
                    val = json.dumps(val)
                values.append(val)
        if fields:
            values.extend([consent_id, CONSENT_TYPES["legal"]])
            safe_db_query(
                f"UPDATE consents SET {', '.join(fields)} WHERE id = ? AND type = ?",
                values,
                commit=True
            )
        cur = safe_db_query(
            'SELECT * FROM consents WHERE id = ? AND type = ?', (consent_id, CONSENT_TYPES["legal"])
        )
        consent = cur.fetchone()
    elif request.method == 'DELETE':
        safe_db_query(
            'DELETE FROM consents WHERE id = ? AND type = ?', (consent_id, CONSENT_TYPES["legal"]), commit=True
        )
        return '', status.HTTP_204_NO_CONTENT

    return jsonify(serialize_consent(consent)), status.HTTP_200_OK
