from flask import Blueprint, jsonify, request, abort, g
from app.db import execute_query
from flasgger import Swagger, swag_from

transactions_bp = Blueprint('transactions', __name__)
DATABASE = 'mockserver.db'

@swag_from('../docs/transactions.yml')

@transactions_bp.route('/transaction-history-v1.0.0/', methods=['GET'])
def transactions():
    try:
        page = max(int(request.args.get('page', 1)), 1)
        page_size = 50
        offset = (page - 1) * page_size
    except ValueError:
        abort(400, description="Invalid pagination parameters")

    cur = execute_query(
        'SELECT * FROM transactions ORDER BY date DESC LIMIT ? OFFSET ?',
        (page_size, offset)
    )

    return jsonify({
        "transactions": [dict(row) for row in cur.fetchall()],
        "page": page,
        "page_size": page_size
    })


@transactions_bp.route('/transaction-history-v1.0.0/<tx_id>', methods=['GET'])
@swag_from('../docs/transactions.yml')
def single_transaction(tx_id):
    cur = execute_query(
        'SELECT * FROM transactions WHERE id = ?',
        (tx_id,)
    )
    tx = cur.fetchone()
    return jsonify(dict(tx)) if tx else abort(404)
