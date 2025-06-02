from flask import Blueprint, jsonify, request
from jsonschema import ValidationError
from flasgger import swag_from
import uuid
import logging
from datetime import datetime
from app.config import (
    RESPONSE_MESSAGES,
    VRP_STATUSES,
    PAGINATION_CONFIG,
    HTTP_STATUS_CODES,
    HTTP_METHODS
)
from app.db import safe_db_query
from app.utils import log_endpoint, serialize_row

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

vrp_bp = Blueprint('vrp', __name__)


def safe_validate(data, schema):
    try:
        validate(data, schema)
        if 'valid_until' in data and data['valid_until'] < datetime.now().isoformat():
            return "Дата valid_until должна быть в будущем"
        return None
    except ValidationError as e:
        logger.warning(f"VRP validation error: {e}")
        return str(e)


@vrp_bp.route('/vrp-v1.3.1/', methods=HTTP_METHODS[:2])
@swag_from('../docs/vrp.yml')
@log_endpoint
def vrp_operations():
    if request.method == 'POST':
        return handle_vrp_creation(request.json)
    return handle_vrp_list(request.args)


def handle_vrp_creation(data):
    error = safe_validate(data, vrp_schema)
    if error:
        return jsonify({
            "error": RESPONSE_MESSAGES["validation_error"],
            "message": error
        }), HTTP_STATUS_CODES["BAD_REQUEST"]

    try:
        vrp_id = str(uuid.uuid4())
        safe_db_query(
            '''INSERT INTO vrps 
            (id, status, max_amount, frequency, valid_until, recipient_account)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (
                vrp_id,
                VRP_STATUSES["active"],
                data['max_amount'],
                data['frequency'],
                data['valid_until'],
                data['recipient_account']
            ),
            commit=True
        )
        cur = safe_db_query('SELECT * FROM vrps WHERE id = ?', (vrp_id,))
        return jsonify(serialize_row(cur.fetchone())), HTTP_STATUS_CODES["CREATED"]

    except Exception as e:
        logger.error(f"VRP creation failed: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]


def handle_vrp_list(args):
    try:
        page = int(args.get('page', 1))
        page_size = int(args.get('page_size', PAGINATION_CONFIG["default_page_size"]))
        page, page_size = validate_pagination(page, page_size)
        offset = (page - 1) * page_size
    except ValueError:
        return jsonify({
            "error": RESPONSE_MESSAGES["validation_error"],
            "message": "Неверные параметры пагинации"
        }), HTTP_STATUS_CODES["BAD_REQUEST"]

    try:
        cur = safe_db_query(
            'SELECT * FROM vrps ORDER BY valid_until DESC LIMIT ? OFFSET ?',
            (page_size, offset)
        )
        vrps = [serialize_row(row) for row in cur.fetchall()]

        return jsonify({
            "vrps": vrps,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "next_page": f"?page={page + 1}&page_size={page_size}" if len(vrps) == page_size else None
            }
        }), HTTP_STATUS_CODES["OK"]

    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]


@vrp_bp.route('/vrp-v1.3.1/<vrp_id>', methods=HTTP_METHODS)
@swag_from('../docs/vrp.yml')
@log_endpoint
def single_vrp(vrp_id):
    try:
        vrp = get_vrp(vrp_id)

        if not vrp:
            return jsonify({"error": RESPONSE_MESSAGES["not_found"]}), HTTP_STATUS_CODES["NOT_FOUND"]

        if request.method == 'PUT':
            return update_vrp(vrp_id, request.json)

        if request.method == 'DELETE':
            return delete_vrp(vrp_id)

        return jsonify(serialize_row(vrp)), HTTP_STATUS_CODES["OK"]

    except Exception as e:
        logger.error(f"VRP operation failed: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["server_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]


def get_vrp(vrp_id):
    cur = safe_db_query('SELECT * FROM vrps WHERE id = ?', (vrp_id,))
    return cur.fetchone() if cur else None


def update_vrp(vrp_id, data):
    error = safe_validate(data, vrp_schema)
    if error:
        return jsonify({
            "error": RESPONSE_MESSAGES["validation_error"],
            "message": error
        }), HTTP_STATUS_CODES["BAD_REQUEST"]

    try:
        safe_db_query(
            '''UPDATE vrps SET 
            max_amount = ?, frequency = ?, valid_until = ?, recipient_account = ?
            WHERE id = ?''',
            (
                data['max_amount'],
                data['frequency'],
                data['valid_until'],
                data['recipient_account'],
                vrp_id
            ),
            commit=True
        )
        cur = safe_db_query('SELECT * FROM vrps WHERE id = ?', (vrp_id,))
        return jsonify(serialize_row(cur.fetchone())), HTTP_STATUS_CODES["OK"]

    except Exception as e:
        logger.error(f"VRP update failed: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]


def delete_vrp(vrp_id):
    try:
        safe_db_query('DELETE FROM vrps WHERE id = ?', (vrp_id,), commit=True)
        return '', HTTP_STATUS_CODES["NO_CONTENT"]

    except Exception as e:
        logger.error(f"VRP deletion failed: {str(e)}")
        return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]


def validate_pagination(page: int, page_size: int) -> tuple:
    page = max(page, 1)
    page_size = min(max(page_size, 1), PAGINATION_CONFIG["max_page_size"])
    return page, page_size
