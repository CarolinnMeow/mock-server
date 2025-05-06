from flask import Blueprint, jsonify, request, abort
from app.services.data_service import data_service
from app.schemas.vrp import vrp_schema
from jsonschema import validate
import uuid

vrp_bp = Blueprint('vrp', __name__)

@vrp_bp.route('/vrp-v1.3.1/', methods=['GET', 'POST'])
def vrp_operations():
    if request.method == 'POST':
        validate(request.json, vrp_schema)
        vrp = {
            "id": str(uuid.uuid4()),
            "status": "ACTIVE",
            **request.json
        }
        data_service.add_vrp(vrp)
        return jsonify(vrp), 201
    return jsonify(data_service.get_vrps())

@vrp_bp.route('/vrp-v1.3.1/<vrp_id>', methods=['GET', 'PUT', 'DELETE'])
def single_vrp(vrp_id):
    vrp = data_service.get_vrp(vrp_id)
    if not vrp:
        abort(404)
    if request.method == 'PUT':
        validate(request.json, vrp_schema)
        vrp.update(request.json)
    elif request.method == 'DELETE':
        data_service.delete_vrp(vrp_id)
        return '', 204
    return jsonify(vrp)
