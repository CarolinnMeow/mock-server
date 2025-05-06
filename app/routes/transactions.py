from flask import Blueprint, jsonify, request, abort
from app.services.data_service import data_service

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/transaction-history-v1.0.0/', methods=['GET'])
def transactions():
    return jsonify({
        "transactions": data_service.get_transactions(),
        "page": request.args.get('page', 1),
        "page_size": 50
    })

@transactions_bp.route('/transaction-history-v1.0.0/<tx_id>', methods=['GET'])
def single_transaction(tx_id):
    tx = data_service.get_transaction(tx_id)
    return jsonify(tx) if tx else abort(404)
