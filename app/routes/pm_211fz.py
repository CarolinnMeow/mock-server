from flask import Blueprint, jsonify, request, abort, g
from app.schemas.pm_211fz import pm_211fz_schema
from jsonschema import validate
import sqlite3
import uuid

pm_211fz_bp = Blueprint('pm_211fz', __name__)
DATABASE = 'mockserver.db'


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@pm_211fz_bp.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def execute_query(query, args=(), commit=False):
    db = get_db()
    cur = db.execute(query, args)
    if commit:
        db.commit()
    return cur


@pm_211fz_bp.route('/pm-211fz-v1.3.1/', methods=['GET', 'POST'])
def pm_211fz():
    if request.method == 'POST':
        validate(request.json, pm_211fz_schema)
        payment_id = str(uuid.uuid4())
        execute_query(
            '''INSERT INTO payments 
            (id, status, type, amount, currency, recipient, created_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)''',
            (
                payment_id,
                "PROCESSING",
                "pm_211fz",
                request.json['amount'],
                request.json['currency'],
                request.json['recipient']
            ),
            commit=True
        )
        cur = execute_query('SELECT * FROM payments WHERE id = ?', (payment_id,))
        return jsonify(dict(cur.fetchone())), 201

    cur = execute_query('SELECT * FROM payments WHERE type = ?', ('pm_211fz',))
    payments = [dict(row) for row in cur.fetchall()]
    return jsonify(payments)


@pm_211fz_bp.route('/pm-211fz-v1.3.1/<payment_id>', methods=['GET', 'PUT', 'DELETE'])
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
