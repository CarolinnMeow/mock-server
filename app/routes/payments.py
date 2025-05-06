from flask import Blueprint, jsonify, request, abort
from app.services.data_service import data_service
from app.schemas.payment import payment_schema
from jsonschema import validate
import uuid
from datetime import datetime

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/payments-v1.3.1/', methods=['POST'])
def create_payment():
    validate(request.json, payment_schema)
    payment = {
        "id": str(uuid.uuid4()),
        "status": "PENDING",
        "created_at": datetime.now().isoformat(),
        **request.json
    }
    data_service.add_payment(payment)
    return jsonify(payment), 201

@payments_bp.route('/payments-v1.3.1/<payment_id>', methods=['GET', 'PUT', 'DELETE'])
def payment_operations(payment_id):
    payment = data_service.get_payment(payment_id)
    if not payment:
        abort(404)
    if request.method == 'PUT':
        payment.update(request.json)
    elif request.method == 'DELETE':
        data_service.delete_payment(payment_id)
        return '', 204
    return jsonify(payment)
