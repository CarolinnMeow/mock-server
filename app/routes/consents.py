from flask import Blueprint, jsonify, request, abort
from app.services.data_service import data_service
from app.schemas.consent import consent_schema
from jsonschema import validate
import uuid

consents_bp = Blueprint('consents', __name__)

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
    data_service.add_consent(consent)
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
    data_service.add_consent(consent)
    return jsonify(consent), 201

@consents_bp.route('/consent-pe-v2.0.0/<consent_id>', methods=['GET', 'PUT', 'DELETE'])
def pe_consent(consent_id):
    consent = data_service.get_consent(consent_id, 'physical_entity')
    if not consent:
        abort(404)
    if request.method == 'PUT':
        consent.update(request.json)
    elif request.method == 'DELETE':
        data_service.delete_consent(consent_id)
        return '', 204
    return jsonify(consent)

@consents_bp.route('/consent-le-v2.0.0/<consent_id>', methods=['GET', 'PUT', 'DELETE'])
def le_consent(consent_id):
    consent = data_service.get_consent(consent_id, 'legal_entity')
    if not consent:
        abort(404)
    if request.method == 'PUT':
        consent.update(request.json)
    elif request.method == 'DELETE':
        data_service.delete_consent(consent_id)
        return '', 204
    return jsonify(consent)
