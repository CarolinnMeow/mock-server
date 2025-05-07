from flask import Blueprint, jsonify, request, abort, g
from app.schemas.payment import payment_schema
from jsonschema import validate
import sqlite3
import uuid
from datetime import datetime

payments_bp = Blueprint('payments', __name__)
DATABASE = 'mockserver.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def execute_query(query, args=(), commit=False):
    db = get_db()
    cur = db.execute(query, args)
    if commit:
        db.commit()
    return cur

@payments_bp.route('/payments-v1.3.1/', methods=['POST'])
def create_payment():
    validate(request.json, payment_schema)
    payment_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    execute_query(
        '''INSERT INTO payments (id, status, created_at, amount, currency, recipient)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (
            payment_id,
            "PENDING",
            created_at,
            request.json['amount'],
            request.json['currency'],
            request.json['recipient']
        ),
        commit=True
    )
    cur = execute_query('SELECT * FROM payments WHERE id = ?', (payment_id,))
    payment = dict(cur.fetchone())
    return jsonify(payment), 201

@payments_bp.route('/payments-v1.3.1/<payment_id>', methods=['GET', 'PUT', 'DELETE'])
def payment_operations(payment_id):
    cur = execute_query('SELECT * FROM payments WHERE id = ?', (payment_id,))
    payment = cur.fetchone()
    if not payment:
        abort(404)
    if request.method == 'PUT':
        validate(request.json, payment_schema)
        execute_query(
            '''UPDATE payments SET amount = ?, currency = ?, recipient = ? WHERE id = ?''',
            (
                request.json['amount'],
                request.json['currency'],
                request.json['recipient'],
                payment_id
            ),
            commit=True
        )
        cur = execute_query('SELECT * FROM payments WHERE id = ?', (payment_id,))
        payment = cur.fetchone()
    elif request.method == 'DELETE':
        execute_query('DELETE FROM payments WHERE id = ?', (payment_id,), commit=True)
        return '', 204
    return jsonify(dict(payment))
