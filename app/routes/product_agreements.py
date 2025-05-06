from flask import Blueprint, jsonify, request, abort
from app.services.data_service import data_service
from app.schemas.product_agreement import product_agreement_schema
from jsonschema import validate
import uuid

product_agreements_bp = Blueprint('product_agreements', __name__)

@product_agreements_bp.route('/product-agreement-consents-v1.0.1/', methods=['GET', 'POST'])
def product_agreements():
    if request.method == 'POST':
        validate(request.json, product_agreement_schema)
        agreement = {
            "id": str(uuid.uuid4()),
            "status": "PENDING",
            **request.json
        }
        data_service.add_product_agreement(agreement)
        return jsonify(agreement), 201
    return jsonify(data_service.get_product_agreements())

@product_agreements_bp.route('/product-agreement-consents-v1.0.1/<agreement_id>', methods=['GET', 'PUT', 'DELETE'])
def single_product_agreement(agreement_id):
    agreement = data_service.get_product_agreement(agreement_id)
    if not agreement:
        abort(404)
    if request.method == 'PUT':
        validate(request.json, product_agreement_schema)
        agreement.update(request.json)
    elif request.method == 'DELETE':
        data_service.delete_product_agreement(agreement_id)
        return '', 204
    return jsonify(agreement)
