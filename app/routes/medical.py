from flask import Blueprint, jsonify, request
from jsonschema import validate, ValidationError
from flasgger import swag_from
import uuid
import logging
from app.schemas.medical import medical_schema
from app.config import (
    RESPONSE_MESSAGES,
    MEDICAL_LIMITS,
    HTTP_STATUS_CODES,
    HTTP_METHODS
)
from app.db import safe_db_query
from app.utils import log_endpoint, serialize_row, require_headers_and_echo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

medical_bp = Blueprint('medical', __name__)


def safe_validate(data, schema):
    try:
        validate(data, schema)
        # Ручная проверка ограничений
        if len(data.get('name', '')) > MEDICAL_LIMITS["max_name_length"]:
            return f"Поле 'name' слишком длинное (максимум {MEDICAL_LIMITS['max_name_length']} символов)"
        if len(data.get('policy_number', '')) > MEDICAL_LIMITS["max_policy_length"]:
            return f"Поле 'policy_number' слишком длинное (максимум {MEDICAL_LIMITS['max_policy_length']} символов)"
        return None
    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return str(e)


@medical_bp.route('/medical-insured-person-v3.0.3/', methods=HTTP_METHODS[:2])
@swag_from('../docs/medical_insured.yml')
@log_endpoint
@require_headers_and_echo
def medical_insured():
    if request.method == 'POST':
        error = safe_validate(request.json, medical_schema)
        if error:
            return jsonify({
                "error": RESPONSE_MESSAGES["validation_error"],
                "message": error
            }), HTTP_STATUS_CODES["BAD_REQUEST"]

        try:
            person_id = str(uuid.uuid4())
            safe_db_query(
                '''INSERT INTO medical_insured 
                (id, name, policy_number, birth_date) 
                VALUES (?, ?, ?, ?)''',
                (
                    person_id,
                    request.json['name'],
                    request.json['policy_number'],
                    request.json['birth_date']
                ),
                commit=True
            )
            cur = safe_db_query('SELECT * FROM medical_insured WHERE id = ?', (person_id,))
            return jsonify(serialize_row(cur.fetchone())), HTTP_STATUS_CODES["CREATED"]

        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]

    # GET
    try:
        cur = safe_db_query('SELECT * FROM medical_insured')
        people = [serialize_row(row) for row in cur.fetchall()] if cur else []
        return jsonify(people), HTTP_STATUS_CODES["OK"]
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]


@medical_bp.route('/medical-insured-person-v3.0.3/<person_id>', methods=HTTP_METHODS)
@swag_from('../docs/medical_insured.yml')
@log_endpoint
@require_headers_and_echo
def single_medical_insured(person_id):
    try:
        cur = safe_db_query('SELECT * FROM medical_insured WHERE id = ?', (person_id,))
        person = cur.fetchone() if cur else None

        if not person:
            return jsonify({"error": RESPONSE_MESSAGES["not_found"]}), HTTP_STATUS_CODES["NOT_FOUND"]

        if request.method == 'PUT':
            error = safe_validate(request.json, medical_schema)
            if error:
                return jsonify({
                    "error": RESPONSE_MESSAGES["validation_error"],
                    "message": error
                }), HTTP_STATUS_CODES["BAD_REQUEST"]

            safe_db_query(
                '''UPDATE medical_insured 
                SET name = ?, policy_number = ?, birth_date = ? 
                WHERE id = ?''',
                (
                    request.json['name'],
                    request.json['policy_number'],
                    request.json['birth_date'],
                    person_id
                ),
                commit=True
            )
            cur = safe_db_query('SELECT * FROM medical_insured WHERE id = ?', (person_id,))
            person = cur.fetchone()

        elif request.method == 'DELETE':
            safe_db_query('DELETE FROM medical_insured WHERE id = ?', (person_id,), commit=True)
            return '', HTTP_STATUS_CODES["NO_CONTENT"]

        return jsonify(serialize_row(person)), HTTP_STATUS_CODES["OK"]

    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]
