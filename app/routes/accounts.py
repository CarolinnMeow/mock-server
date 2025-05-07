from flask import Blueprint, jsonify, request, abort, g
from app.schemas.account import physical_account_schema, legal_account_schema
from jsonschema import validate
from app.db import get_db, execute_query
import uuid

accounts_bp = Blueprint('accounts', __name__)
DATABASE = 'mockserver.db'

@accounts_bp.route('/accounts-v1.3.3/', methods=['GET', 'POST'])
def physical_accounts():
    if request.method == 'GET':
        cur = execute_query('''
            SELECT * FROM accounts 
            WHERE type = 'physical_entity'
        ''')
        return jsonify([dict(row) for row in cur.fetchall()])

    if request.method == 'POST':
        validate(request.json, physical_account_schema)
        account_id = str(uuid.uuid4())

        execute_query('''
            INSERT INTO accounts 
            (id, balance, currency, type, status, owner)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            account_id,
            request.json['balance'],
            request.json['currency'],
            'physical_entity',
            request.json['status'],
            request.json['owner']
        ), commit=True)

        return jsonify({"id": account_id}), 201


@accounts_bp.route('/accounts-v1.3.3/<account_id>', methods=['GET', 'PUT', 'DELETE'])
def physical_account(account_id):
    if request.method == 'GET':
        cur = execute_query('''
            SELECT * FROM accounts 
            WHERE id = ? AND type = 'physical_entity'
        ''', (account_id,))
        account = cur.fetchone()
        return jsonify(dict(account)) if account else abort(404)

    if request.method == 'PUT':
        validate(request.json, physical_account_schema)
        execute_query('''
            UPDATE accounts SET
            balance = ?, 
            currency = ?,
            status = ?,
            owner = ?
            WHERE id = ? AND type = 'physical_entity'
        ''', (
            request.json['balance'],
            request.json['currency'],
            request.json['status'],
            request.json['owner'],
            account_id
        ), commit=True)
        return jsonify({"status": "updated"})

    if request.method == 'DELETE':
        execute_query('''
            DELETE FROM accounts 
            WHERE id = ? AND type = 'physical_entity'
        ''', (account_id,), commit=True)
        return '', 204


@accounts_bp.route('/accounts-le-v2.0.0/', methods=['GET', 'POST'])
def legal_accounts():
    if request.method == 'GET':
        cur = execute_query('''
            SELECT * FROM accounts 
            WHERE type = 'legal_entity'
        ''')
        return jsonify([dict(row) for row in cur.fetchall()])

    if request.method == 'POST':
        validate(request.json, legal_account_schema)
        account_id = str(uuid.uuid4())

        execute_query('''
            INSERT INTO accounts 
            (id, balance, currency, type, status, company)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            account_id,
            request.json['balance'],
            request.json['currency'],
            'legal_entity',
            request.json['status'],
            request.json['company']
        ), commit=True)

        return jsonify({"id": account_id}), 201


@accounts_bp.route('/accounts-le-v2.0.0/<account_id>', methods=['GET', 'PUT', 'DELETE'])
def legal_account(account_id):
    if request.method == 'GET':
        cur = execute_query('''
            SELECT * FROM accounts 
            WHERE id = ? AND type = 'legal_entity'
        ''', (account_id,))
        account = cur.fetchone()
        return jsonify(dict(account)) if account else abort(404)

    if request.method == 'PUT':
        validate(request.json, legal_account_schema)
        execute_query('''
            UPDATE accounts SET
            balance = ?, 
            currency = ?,
            status = ?,
            company = ?
            WHERE id = ? AND type = 'legal_entity'
        ''', (
            request.json['balance'],
            request.json['currency'],
            request.json['status'],
            request.json['company'],
            account_id
        ), commit=True)
        return jsonify({"status": "updated"})

    if request.method == 'DELETE':
        execute_query('''
            DELETE FROM accounts 
            WHERE id = ? AND type = 'legal_entity'
        ''', (account_id,), commit=True)
        return '', 204
