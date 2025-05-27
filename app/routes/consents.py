from flask import Blueprint, jsonify, request, abort, g
from app.schemas.consent import consent_schema
from jsonschema import validate
from flasgger import Swagger, swag_from
from app.db import execute_query
import uuid
import json

consents_bp = Blueprint('consents', __name__)
DATABASE = 'mockserver.db'

@swag_from('../docs/consents.yml')

@consents_bp.route('/consent-pe-v2.0.0/', methods=['POST'])
def create_pe_consent():
    validate(request.json, consent_schema)
    consent_id = str(uuid.uuid4())
    consent = {
        "id": consent_id,
        "type": "physical_entity",
        "status": "ACTIVE",
        **request.json
    }
    execute_query(
        '''INSERT INTO consents (id, type, status, tpp_id, permissions) VALUES (?, ?, ?, ?, ?)''',
        (
            consent_id,
            "physical_entity",
            "ACTIVE",
            consent.get('tpp_id'),
            json.dumps(consent.get('permissions', []))
        ),
        commit=True
    )
    return jsonify(consent), 201

@consents_bp.route('/consent-le-v2.0.0/', methods=['POST'])
def create_le_consent():
    validate(request.json, consent_schema)
    consent_id = str(uuid.uuid4())
    consent = {
        "id": consent_id,
        "type": "legal_entity",
        "status": "ACTIVE",
        **request.json
    }
    execute_query(
        '''INSERT INTO consents (id, type, status, tpp_id, permissions) VALUES (?, ?, ?, ?, ?)''',
        (
            consent_id,
            "legal_entity",
            "ACTIVE",
            consent.get('tpp_id'),
            json.dumps(consent.get('permissions', []))
        ),
        commit=True
    )
    return jsonify(consent), 201

@consents_bp.route('/consent-pe-v2.0.0/<consent_id>', methods=['GET', 'PUT', 'DELETE'])
def pe_consent(consent_id):
    cur = execute_query(
        'SELECT * FROM consents WHERE id = ? AND type = ?', (consent_id, 'physical_entity')
    )
    consent = cur.fetchone()
    if not consent:
        abort(404)
    if request.method == 'PUT':
        # Обновляем только разрешённые поля
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
            values.extend([consent_id, 'physical_entity'])
            execute_query(
                f"UPDATE consents SET {', '.join(fields)} WHERE id = ? AND type = ?",
                values,
                commit=True
            )
        cur = execute_query(
            'SELECT * FROM consents WHERE id = ? AND type = ?', (consent_id, 'physical_entity')
        )
        consent = cur.fetchone()
    elif request.method == 'DELETE':
        execute_query(
            'DELETE FROM consents WHERE id = ? AND type = ?', (consent_id, 'physical_entity'), commit=True
        )
        return '', 204
    # Преобразуем permissions обратно в список
    result = dict(consent)
    result['permissions'] = json.loads(result['permissions']) if result['permissions'] else []
    return jsonify(result)

@consents_bp.route('/consent-le-v2.0.0/<consent_id>', methods=['GET', 'PUT', 'DELETE'])
def le_consent(consent_id):
    cur = execute_query(
        'SELECT * FROM consents WHERE id = ? AND type = ?', (consent_id, 'legal_entity')
    )
    consent = cur.fetchone()
    if not consent:
        abort(404)
    if request.method == 'PUT':
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
            values.extend([consent_id, 'legal_entity'])
            execute_query(
                f"UPDATE consents SET {', '.join(fields)} WHERE id = ? AND type = ?",
                values,
                commit=True
            )
        cur = execute_query(
            'SELECT * FROM consents WHERE id = ? AND type = ?', (consent_id, 'legal_entity')
        )
        consent = cur.fetchone()
    elif request.method == 'DELETE':
        execute_query(
            'DELETE FROM consents WHERE id = ? AND type = ?', (consent_id, 'legal_entity'), commit=True
        )
        return '', 204
    result = dict(consent)
    result['permissions'] = json.loads(result['permissions']) if result['permissions'] else []
    return jsonify(result)
