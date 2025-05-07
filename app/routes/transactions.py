from flask import Blueprint, jsonify, request, abort, g
import sqlite3

transactions_bp = Blueprint('transactions', __name__)
DATABASE = 'mockserver.db'


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


def execute_query(query, args=()):
    return get_db().execute(query, args)


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
def single_transaction(tx_id):
    cur = execute_query(
        'SELECT * FROM transactions WHERE id = ?',
        (tx_id,)
    )
    tx = cur.fetchone()
    return jsonify(dict(tx)) if tx else abort(404)
