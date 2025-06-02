from flask import Blueprint, jsonify, request
from flasgger import swag_from
import logging
from app.config import (
    RESPONSE_MESSAGES,
    PAGINATION_CONFIG,
    HTTP_STATUS_CODES,
    HTTP_METHODS
)
from app.db import safe_db_query
from app.utils import log_endpoint, serialize_row

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

transactions_bp = Blueprint('transactions', __name__)


def validate_pagination(page: int, page_size: int) -> tuple:
    page = max(page, 1)
    page_size = min(max(page_size, 1), PAGINATION_CONFIG["max_page_size"])
    return page, page_size


@transactions_bp.route('/transaction-history-v1.0.0/', methods=HTTP_METHODS[:1])
@swag_from('../docs/transactions.yml')
@log_endpoint
def transactions():
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', PAGINATION_CONFIG["default_page_size"]))
        page, page_size = validate_pagination(page, page_size)
        offset = (page - 1) * page_size
    except ValueError:
        return jsonify({
            "error": RESPONSE_MESSAGES["validation_error"],
            "message": "Invalid pagination parameters"
        }), HTTP_STATUS_CODES["BAD_REQUEST"]

    try:
        cur = safe_db_query(
            'SELECT * FROM transactions ORDER BY date DESC LIMIT ? OFFSET ?',
            (page_size, offset)
        )
        transactions_data = [serialize_row(row) for row in cur.fetchall()]

        return jsonify({
            "transactions": transactions_data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "next_page": f"?page={page + 1}&page_size={page_size}" if len(transactions_data) == page_size else None
            }
        }), HTTP_STATUS_CODES["OK"]

    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]


@transactions_bp.route('/transaction-history-v1.0.0/<tx_id>', methods=HTTP_METHODS[:1])
@swag_from('../docs/transactions.yml')
@log_endpoint
def single_transaction(tx_id):
    try:
        cur = safe_db_query(
            'SELECT * FROM transactions WHERE id = ?',
            (tx_id,)
        )
        tx = cur.fetchone() if cur else None

        if not tx:
            return jsonify({"error": RESPONSE_MESSAGES["not_found"]}), HTTP_STATUS_CODES["NOT_FOUND"]

        return jsonify(serialize_row(tx)), HTTP_STATUS_CODES["OK"]

    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]
