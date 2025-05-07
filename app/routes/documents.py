from flask import Blueprint, jsonify, request, abort, g
from app.schemas.document import bank_doc_schema, insurance_doc_schema
from jsonschema import validate
from app.db import get_db, execute_query
import uuid

documents_bp = Blueprint('documents', __name__)
DATABASE = 'mockserver.db'

@documents_bp.route('/bank-doc-v1.0.1/', methods=['GET', 'POST'])
def bank_docs():
    if request.method == 'POST':
        validate(request.json, bank_doc_schema)
        doc_id = str(uuid.uuid4())
        execute_query(
            '''INSERT INTO bank_docs (id, type, content, signature, created_at)
               VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)''',
            (
                doc_id,
                request.json['type'],
                request.json['content'],
                request.json['signature']
            ),
            commit=True
        )
        cur = execute_query('SELECT * FROM bank_docs WHERE id = ?', (doc_id,))
        doc = cur.fetchone()
        return jsonify(dict(doc)), 201
    else:
        cur = execute_query('SELECT * FROM bank_docs')
        docs = [dict(row) for row in cur.fetchall()]
        return jsonify(docs)

@documents_bp.route('/bank-doc-v1.0.1/<doc_id>', methods=['GET', 'PUT', 'DELETE'])
def bank_doc(doc_id):
    cur = execute_query('SELECT * FROM bank_docs WHERE id = ?', (doc_id,))
    doc = cur.fetchone()
    if not doc:
        abort(404)
    if request.method == 'PUT':
        validate(request.json, bank_doc_schema)
        execute_query(
            '''UPDATE bank_docs SET type = ?, content = ?, signature = ? WHERE id = ?''',
            (
                request.json['type'],
                request.json['content'],
                request.json['signature'],
                doc_id
            ),
            commit=True
        )
        cur = execute_query('SELECT * FROM bank_docs WHERE id = ?', (doc_id,))
        doc = cur.fetchone()
    elif request.method == 'DELETE':
        execute_query('DELETE FROM bank_docs WHERE id = ?', (doc_id,), commit=True)
        return '', 204
    return jsonify(dict(doc))

@documents_bp.route('/insurance-doc-v1.0.1/', methods=['GET', 'POST'])
def insurance_docs():
    if request.method == 'POST':
        validate(request.json, insurance_doc_schema)
        doc_id = str(uuid.uuid4())
        execute_query(
            '''INSERT INTO insurance_docs (id, type, content, policy_number, valid_until, created_at)
               VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)''',
            (
                doc_id,
                request.json['type'],
                request.json['content'],
                request.json['policy_number'],
                request.json['valid_until']
            ),
            commit=True
        )
        cur = execute_query('SELECT * FROM insurance_docs WHERE id = ?', (doc_id,))
        doc = cur.fetchone()
        return jsonify(dict(doc)), 201
    else:
        cur = execute_query('SELECT * FROM insurance_docs')
        docs = [dict(row) for row in cur.fetchall()]
        return jsonify(docs)

@documents_bp.route('/insurance-doc-v1.0.1/<doc_id>', methods=['GET', 'PUT', 'DELETE'])
def insurance_doc(doc_id):
    cur = execute_query('SELECT * FROM insurance_docs WHERE id = ?', (doc_id,))
    doc = cur.fetchone()
    if not doc:
        abort(404)
    if request.method == 'PUT':
        validate(request.json, insurance_doc_schema)
        execute_query(
            '''UPDATE insurance_docs SET type = ?, content = ?, policy_number = ?, valid_until = ? WHERE id = ?''',
            (
                request.json['type'],
                request.json['content'],
                request.json['policy_number'],
                request.json['valid_until'],
                doc_id
            ),
            commit=True
        )
        cur = execute_query('SELECT * FROM insurance_docs WHERE id = ?', (doc_id,))
        doc = cur.fetchone()
    elif request.method == 'DELETE':
        execute_query('DELETE FROM insurance_docs WHERE id = ?', (doc_id,), commit=True)
        return '', 204
    return jsonify(dict(doc))
