from flask import Blueprint, jsonify, request
from flask_api import status
from flasgger import swag_from
import logging
from app.config import RESPONSE_MESSAGES, PAGINATION_CONFIG
from app.db import execute_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

transactions_bp = Blueprint('transactions', __name__)


def validate_pagination(page: int, page_size: int) -> tuple:
    page = max(page, 1)
    page_size = min(max(page_size, 1), PAGINATION_CONFIG["max_page_size"])
    return page, page_size


def serialize_transaction(row):
    return dict(row) if row else {}


@transactions_bp.route('/transaction-history-v1.0.0/', methods=['GET'])
@swag_from('../docs/transactions.yml')
def transactions():
    logger.info(f"GET {request.path}")

    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', PAGINATION_CONFIG["default_page_size"]))
        page, page_size = validate_pagination(page, page_size)
        offset = (page - 1) * page_size
    except ValueError:
        logger.warning("Invalid pagination parameters")
        return jsonify({
            "error": RESPONSE_MESSAGES["validation_error"],
            "message": "Invalid pagination parameters"
        }), status.HTTP_400_BAD_REQUEST

    cur = safe_db_query(
        'SELECT * FROM transactions ORDER BY date DESC LIMIT ? OFFSET ?',
        (page_size, offset)
    )

    if not cur:
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), status.HTTP_500_INTERNAL_SERVER_ERROR

    return jsonify({
        "transactions": [serialize_transaction(row) for row in cur.fetchall()],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "next_page": f"?page={page + 1}&page_size={page_size}" if cur.rowcount == page_size else None
        }
    }), status.HTTP_200_OK


@transactions_bp.route('/transaction-history-v1.0.0/<tx_id>', methods=['GET'])
@swag_from('../docs/transactions.yml')
def single_transaction(tx_id):
    logger.info(f"GET {request.path} | id={tx_id}")

    cur = safe_db_query(
        'SELECT * FROM transactions WHERE id = ?',
        (tx_id,)
    )

    if not cur:
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), status.HTTP_500_INTERNAL_SERVER_ERROR

    tx = cur.fetchone()
    if not tx:
        return jsonify({"error": RESPONSE_MESSAGES["not_found"]}), status.HTTP_404_NOT_FOUND

    return jsonify(serialize_transaction(tx)), status.HTTP_200_OK
