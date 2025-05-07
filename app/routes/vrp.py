from flask import Blueprint, jsonify, request, abort, g
from app.schemas.vrp import vrp_schema
from jsonschema import validate
import sqlite3
import uuid

vrp_bp = Blueprint('vrp', __name__)
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


@vrp_bp.route('/vrp-v1.3.1/', methods=['GET', 'POST'])
def vrp_operations():
    if request.method == 'POST':
        validate(request.json, vrp_schema)
        vrp_id = str(uuid.uuid4())
        execute_query(
            '''INSERT INTO vrps 
            (id, status, max_amount, frequency, valid_until, recipient_account)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (
                vrp_id,
                "ACTIVE",
                request.json['max_amount'],
                request.json['frequency'],
                request.json['valid_until'],
                request.json['recipient_account']
            ),
            commit=True
        )
        cur = execute_query('SELECT * FROM vrps WHERE id = ?', (vrp_id,))
        return jsonify(dict(cur.fetchone())), 201

    cur = execute_query('SELECT * FROM vrps')
    vrps = [dict(row) for row in cur.fetchall()]
    return jsonify(vrps)


@vrp_bp.route('/vrp-v1.3.1/<vrp_id>', methods=['GET', 'PUT', 'DELETE'])
def single_vrp(vrp_id):
    cur = execute_query('SELECT * FROM vrps WHERE id = ?', (vrp_id,))
    vrp = cur.fetchone()

    if not vrp:
        abort(404)

    if request.method == 'PUT':
        validate(request.json, vrp_schema)
        execute_query(
            '''UPDATE vrps SET 
            max_amount = ?, frequency = ?, valid_until = ?, recipient_account = ?
            WHERE id = ?''',
            (
                request.json['max_amount'],
                request.json['frequency'],
                request.json['valid_until'],
                request.json['recipient_account'],
                vrp_id
            ),
            commit=True
        )
        cur = execute_query('SELECT * FROM vrps WHERE id = ?', (vrp_id,))
        vrp = cur.fetchone()

    elif request.method == 'DELETE':
        execute_query('DELETE FROM vrps WHERE id = ?', (vrp_id,), commit=True)
        return '', 204

    return jsonify(dict(vrp))
