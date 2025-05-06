from flask import Blueprint, jsonify, request, abort
from app.services.data_service import data_service
from app.schemas.pm_211fz import pm_211fz_schema
from jsonschema import validate
import uuid

pm_211fz_bp = Blueprint('pm_211fz', __name__)

@pm_211fz_bp.route('/pm-211fz-v1.3.1/', methods=['GET', 'POST'])
def pm_211fz():
    if request.method == 'POST':
        validate(request.json, pm_211fz_schema)
        payment = {
            "id": str(uuid.uuid4()),
            "status": "PROCESSING",
            "type": "pm_211fz",
            **request.json
        }
        data_service.add_payment(payment)
        return jsonify(payment), 201
    return jsonify([p for p in data_service.get_payments() if p.get('type') == 'pm_211fz'])

@pm_211fz_bp.route('/pm-211fz-v1.3.1/<payment_id>', methods=['GET', 'PUT', 'DELETE'])
def single_pm_211fz(payment_id):
    payment = next((p for p in data_service.get_payments() if p['id'] == payment_id and p.get('type') == 'pm_211fz'), None)
    if not payment:
        abort(404)
    if request.method == 'PUT':
        validate(request.json, pm_211fz_schema)
        payment.update(request.json)
    elif request.method == 'DELETE':
        data_service.delete_payment(payment_id)
        return '', 204
    return jsonify(payment)
