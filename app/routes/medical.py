from flask import Blueprint, jsonify, request
from flask_api import status
from app.schemas.medical import medical_schema
from jsonschema import validate, ValidationError
from flasgger import swag_from
from app.db import execute_query
import uuid
import logging
from app.config import RESPONSE_MESSAGES, MEDICAL_LIMITS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

medical_bp = Blueprint('medical', __name__)

def safe_validate(data, schema):
    try:
        validate(data, schema)
        # Пример ручной проверки ограничений
        if len(data.get('name', '')) > MEDICAL_LIMITS["max_name_length"]:
            return f"Поле 'name' слишком длинное (максимум {MEDICAL_LIMITS['max_name_length']} символов)"
        if len(data.get('policy_number', '')) > MEDICAL_LIMITS["max_policy_length"]:
            return f"Поле 'policy_number' слишком длинное (максимум {MEDICAL_LIMITS['max_policy_length']} символов)"
        return None
    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return str(e)

def safe_db_query(query, params=(), commit=False):
    try:
        return execute_query(query, params, commit)
    except Exception as e:
        logger.error(f"DB error: {e}")
        return None

def serialize_person(row):
    return dict(row)

@swag_from('../docs/medical_insured.yml')
@medical_bp.route('/medical-insured-person-v3.0.3/', methods=['GET', 'POST'])
def medical_insured():
    logger.info(f"{request.method} {request.path}")

    if request.method == 'POST':
        error = safe_validate(request.json, medical_schema)
        if error:
            return jsonify({"error": RESPONSE_MESSAGES["validation_error"], "message": error}), status.HTTP_400_BAD_REQUEST

        person_id = str(uuid.uuid4())
        result = safe_db_query(
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
        if result is None:
            return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), status.HTTP_500_INTERNAL_SERVER_ERROR

        cur = safe_db_query('SELECT * FROM medical_insured WHERE id = ?', (person_id,))
        person = cur.fetchone() if cur else None
        return jsonify(serialize_person(person)), status.HTTP_201_CREATED

    cur = safe_db_query('SELECT * FROM medical_insured')
    people = [serialize_person(row) for row in cur.fetchall()] if cur else []
    return jsonify(people), status.HTTP_200_OK

@medical_bp.route('/medical-insured-person-v3.0.3/<person_id>', methods=['GET', 'PUT', 'DELETE'])
@swag_from('../docs/medical_insured.yml')
def single_medical_insured(person_id):
    logger.info(f"{request.method} {request.path} | id={person_id}")

    cur = safe_db_query('SELECT * FROM medical_insured WHERE id = ?', (person_id,))
    person = cur.fetchone() if cur else None

    if not person:
        return jsonify({"error": RESPONSE_MESSAGES["not_found"]}), status.HTTP_404_NOT_FOUND

    if request.method == 'PUT':
        error = safe_validate(request.json, medical_schema)
        if error:
            return jsonify({"error": RESPONSE_MESSAGES["validation_error"], "message": error}), status.HTTP_400_BAD_REQUEST

        result = safe_db_query(
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
        if result is None:
            return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), status.HTTP_500_INTERNAL_SERVER_ERROR

        cur = safe_db_query('SELECT * FROM medical_insured WHERE id = ?', (person_id,))
        person = cur.fetchone() if cur else None

    elif request.method == 'DELETE':
        result = safe_db_query('DELETE FROM medical_insured WHERE id = ?', (person_id,), commit=True)
        if result is None:
            return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), status.HTTP_500_INTERNAL_SERVER_ERROR
        return '', status.HTTP_204_NO_CONTENT

    return jsonify(serialize_person(person)), status.HTTP_200_OK
