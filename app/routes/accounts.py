from flask import Blueprint, jsonify, request, abort
from app.services.data_service import data_service
from app.schemas.account import physical_account_schema, legal_account_schema
from jsonschema import validate

accounts_bp = Blueprint('accounts', __name__)

@accounts_bp.route('/accounts-v1.3.3/', methods=['GET', 'POST'])
def physical_accounts():
    if request.method == 'GET':
        return jsonify(data_service.get_accounts('physical_entity'))
    if request.method == 'POST':
        validate(request.json, physical_account_schema)
        account = data_service.add_account(request.json, 'physical_entity')
        return jsonify(account), 201

@accounts_bp.route('/accounts-v1.3.3/<account_id>', methods=['GET', 'PUT', 'DELETE'])
def physical_account(account_id):
    account = data_service.get_account(account_id, 'physical_entity')
    if not account:
        abort(404)
    if request.method == 'PUT':
        account.update(request.json)
    elif request.method == 'DELETE':
        data_service.delete_account(account_id, 'physical_entity')
        return '', 204
    return jsonify(account)

@accounts_bp.route('/accounts-le-v2.0.0/', methods=['GET', 'POST'])
def legal_accounts():
    if request.method == 'GET':
        return jsonify(data_service.get_accounts('legal_entity'))
    if request.method == 'POST':
        validate(request.json, legal_account_schema)
        account = data_service.add_account(request.json, 'legal_entity')
        return jsonify(account), 201

@accounts_bp.route('/accounts-le-v2.0.0/<account_id>', methods=['GET', 'PUT', 'DELETE'])
def legal_account(account_id):
    account = data_service.get_account(account_id, 'legal_entity')
    if not account:
        abort(404)
    if request.method == 'PUT':
        account.update(request.json)
    elif request.method == 'DELETE':
        data_service.delete_account(account_id, 'legal_entity')
        return '', 204
    return jsonify(account)
