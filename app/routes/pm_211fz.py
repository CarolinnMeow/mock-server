from flask import Blueprint, jsonify, request, abort, g
from app.schemas.pm_211fz import pm_211fz_schema
from jsonschema import validate
from flasgger import Swagger, swag_from
from app.db import execute_query
import uuid

pm_211fz_bp = Blueprint('pm_211fz', __name__)
DATABASE = 'mockserver.db'

@swag_from('../docs/pm_211fz.yml')

@pm_211fz_bp.route('/pm-211fz-v1.3.1/', methods=['GET', 'POST'])
def pm_211fz():
    if request.method == 'POST':
        validate(request.json, pm_211fz_schema)
        payment_id = str(uuid.uuid4())
        execute_query(
            '''INSERT INTO payments 
            (id, status, type, amount, currency, recipient, purpose, budget_code, created_at, account_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)''',
            (
                payment_id,
                "PENDING",
                "pm_211fz",
                request.json['amount'],
                request.json['currency'],
                request.json['recipient'],
                request.json['purpose'],
                request.json['budget_code'],
                request.json['account_id']   # <-- добавлено!
            ),
            commit=True
        )
        cur = execute_query('SELECT * FROM payments WHERE id = ?', (payment_id,))
        return jsonify(dict(cur.fetchone())), 201

    # GET-запрос - без изменений
    cur = execute_query('SELECT * FROM payments WHERE type = ?', ('pm_211fz',))
    payments = [dict(row) for row in cur.fetchall()]
    return jsonify(payments)



@pm_211fz_bp.route('/pm-211fz-v1.3.1/<payment_id>', methods=['GET', 'PUT', 'DELETE'])
@swag_from('../docs/pm_211fz.yml')
def single_pm_211fz(payment_id):
    cur = execute_query(
        'SELECT * FROM payments WHERE id = ? AND type = ?',
        (payment_id, 'pm_211fz')
    )
    payment = cur.fetchone()

    if not payment:
        abort(404)

    if request.method == 'PUT':
        validate(request.json, pm_211fz_schema)
        execute_query(
            '''UPDATE payments SET 
            amount = ?, currency = ?, recipient = ? 
            WHERE id = ? AND type = ?''',
            (
                request.json['amount'],
                request.json['currency'],
                request.json['recipient'],
                payment_id,
                'pm_211fz'
            ),
            commit=True
        )
        cur = execute_query('SELECT * FROM payments WHERE id = ?', (payment_id,))
        payment = cur.fetchone()

    elif request.method == 'DELETE':
        execute_query(
            'DELETE FROM payments WHERE id = ? AND type = ?',
            (payment_id, 'pm_211fz'),
            commit=True
        )
        return '', 204

    return jsonify(dict(payment))
