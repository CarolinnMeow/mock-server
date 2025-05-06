from flask import Blueprint, jsonify, request, abort
from app.services.data_service import data_service
from app.schemas.medical import medical_schema
from jsonschema import validate
import uuid

medical_bp = Blueprint('medical', __name__)

@medical_bp.route('/medical-insured-person-v3.0.3/', methods=['GET', 'POST'])
def medical_insured():
    if request.method == 'POST':
        validate(request.json, medical_schema)
        person = {
            "id": str(uuid.uuid4()),
            **request.json
        }
        data_service.add_medical_insured(person)
        return jsonify(person), 201
    return jsonify(data_service.get_medical_insured())

@medical_bp.route('/medical-insured-person-v3.0.3/<person_id>', methods=['GET', 'PUT', 'DELETE'])
def single_medical_insured(person_id):
    person = data_service.get_medical_insured_by_id(person_id)
    if not person:
        abort(404)
    if request.method == 'PUT':
        validate(request.json, medical_schema)
        person.update(request.json)
    elif request.method == 'DELETE':
        data_service.delete_medical_insured(person_id)
        return '', 204
    return jsonify(person)
