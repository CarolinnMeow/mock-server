from flask import Blueprint, jsonify, request, abort, g
from app.schemas.product_agreement import product_agreement_schema
from jsonschema import validate
from app.db import get_db, execute_query
import uuid
import json

product_agreements_bp = Blueprint('product_agreements', __name__)
DATABASE = 'mockserver.db'

@product_agreements_bp.route('/product-agreement-consents-v1.0.1/', methods=['GET', 'POST'])
def product_agreements():
    if request.method == 'POST':
        validate(request.json, product_agreement_schema)
        agreement_id = str(uuid.uuid4())
        terms_str = json.dumps(request.json['terms'])
        execute_query(
            '''INSERT INTO product_agreements (id, product_type, terms, status)
               VALUES (?, ?, ?, ?)''',
            (
                agreement_id,
                request.json['product_type'],
                terms_str,
                "ACTIVE"
            ),
            commit=True
        )
        cur = execute_query(
            'SELECT * FROM product_agreements WHERE id = ?',
            (agreement_id,)
        )
        return jsonify(dict(cur.fetchone())), 201

    cur = execute_query('SELECT * FROM product_agreements')
    agreements = [dict(row) for row in cur.fetchall()]
    return jsonify(agreements)


@product_agreements_bp.route('/product-agreement-consents-v1.0.1/<agreement_id>', methods=['GET', 'PUT', 'DELETE'])
def single_product_agreement(agreement_id):
    cur = execute_query(
        'SELECT * FROM product_agreements WHERE id = ?',
        (agreement_id,)
    )
    agreement = cur.fetchone()

    if not agreement:
        abort(404)

    if request.method == 'PUT':
        validate(request.json, product_agreement_schema)
        execute_query(
            '''UPDATE product_agreements 
            SET product_type = ?, terms = ? 
            WHERE id = ?''',
            (
                request.json['product_type'],
                request.json['terms'],
                agreement_id
            ),
            commit=True
        )
        cur = execute_query(
            'SELECT * FROM product_agreements WHERE id = ?',
            (agreement_id,)
        )
        agreement = cur.fetchone()

    elif request.method == 'DELETE':
        execute_query(
            'DELETE FROM product_agreements WHERE id = ?',
            (agreement_id,),
            commit=True
        )
        return '', 204

    return jsonify(dict(agreement))
