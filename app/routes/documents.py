from flask import Blueprint, jsonify, request, abort
from app.services.data_service import data_service
from app.schemas.document import bank_doc_schema, insurance_doc_schema
from jsonschema import validate

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/bank-doc-v1.0.1/', methods=['GET', 'POST'])
def bank_docs():
    if request.method == 'POST':
        validate(request.json, bank_doc_schema)
        doc = data_service.add_bank_doc(request.json)
        return jsonify(doc), 201
    return jsonify(list(data_service.get_bank_docs()))

@documents_bp.route('/bank-doc-v1.0.1/<doc_id>', methods=['GET', 'PUT', 'DELETE'])
def bank_doc(doc_id):
    doc = data_service.get_bank_doc(doc_id)
    if not doc:
        abort(404)
    if request.method == 'PUT':
        doc.update(request.json)
    elif request.method == 'DELETE':
        data_service.delete_bank_doc(doc_id)
        return '', 204
    return jsonify(doc)

@documents_bp.route('/insurance-doc-v1.0.1/', methods=['GET', 'POST'])
def insurance_docs():
    if request.method == 'POST':
        validate(request.json, insurance_doc_schema)
        doc = data_service.add_insurance_doc(request.json)
        return jsonify(doc), 201
    return jsonify(list(data_service.get_insurance_docs()))

@documents_bp.route('/insurance-doc-v1.0.1/<doc_id>', methods=['GET', 'PUT', 'DELETE'])
def insurance_doc(doc_id):
    doc = data_service.get_insurance_doc(doc_id)
    if not doc:
        abort(404)
    if request.method == 'PUT':
        doc.update(request.json)
    elif request.method == 'DELETE':
        data_service.delete_insurance_doc(doc_id)
        return '', 204
    return jsonify(doc)
