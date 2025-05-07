from flask import Blueprint, jsonify, request, abort, g
from app.schemas.medical import medical_schema
from jsonschema import validate
import sqlite3
import uuid

medical_bp = Blueprint('medical', __name__)
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


@medical_bp.route('/medical-insured-person-v3.0.3/', methods=['GET', 'POST'])
def medical_insured():
    if request.method == 'POST':
        validate(request.json, medical_schema)
        person_id = str(uuid.uuid4())
        execute_query(
            '''INSERT INTO medical_insured 
            (id, name, policy_number, birth_date) 
            VALUES (?, ?, ?, ?)''',
            (
                person_id,
                request.json['name'],
                request.json['policy_number'],
                request.json['birth_date']
            ),
            commit=True
        )
        cur = execute_query(
            'SELECT * FROM medical_insured WHERE id = ?',
            (person_id,)
        )
        person = dict(cur.fetchone())
        return jsonify(person), 201

    cur = execute_query('SELECT * FROM medical_insured')
    people = [dict(row) for row in cur.fetchall()]
    return jsonify(people)


@medical_bp.route('/medical-insured-person-v3.0.3/<person_id>', methods=['GET', 'PUT', 'DELETE'])
def single_medical_insured(person_id):
    cur = execute_query(
        'SELECT * FROM medical_insured WHERE id = ?',
        (person_id,)
    )
    person = cur.fetchone()

    if not person:
        abort(404)

    if request.method == 'PUT':
        validate(request.json, medical_schema)
        execute_query(
            '''UPDATE medical_insured 
            SET name = ?, policy_number = ?, birth_date = ? 
            WHERE id = ?''',
            (
                request.json['name'],
                request.json['policy_number'],
                request.json['birth_date'],
                person_id
            ),
            commit=True
        )
        cur = execute_query(
            'SELECT * FROM medical_insured WHERE id = ?',
            (person_id,)
        )
        person = cur.fetchone()

    elif request.method == 'DELETE':
        execute_query(
            'DELETE FROM medical_insured WHERE id = ?',
            (person_id,),
            commit=True
        )
        return '', 204

    return jsonify(dict(person))
