from flask import Blueprint, jsonify, request
from flask_api import status
from jsonschema import ValidationError
from flasgger import swag_from
import uuid
import logging
from app.config import RESPONSE_MESSAGES, VRP_STATUSES, PAGINATION_CONFIG
from app.schemas.vrp import vrp_schema
from app.db import execute_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

vrp_bp = Blueprint('vrp', __name__)


def safe_validate(data, schema):
    try:
        validate(data, schema)
        # Дополнительная проверка даты valid_until
        if 'valid_until' in data and data['valid_until'] < datetime.now().isoformat():
            return "Дата valid_until должна быть в будущем"
        return None
    except ValidationError as e:
        logger.warning(f"VRP validation error: {e}")
        return str(e)


def serialize_vrp(row):
    if not row:
        return {}
    return dict(row)


@vrp_bp.route('/vrp-v1.3.1/', methods=['GET', 'POST'])
@swag_from('../docs/vrp.yml')
def vrp_operations():
    logger.info(f"{request.method} {request.path}")

    if request.method == 'POST':
        error = safe_validate(request.json, vrp_schema)
        if error:
            return jsonify({
                "error": RESPONSE_MESSAGES["validation_error"],
                "message": error
            }), status.HTTP_400_BAD_REQUEST

        vrp_id = str(uuid.uuid4())
        result = safe_db_query(
            '''INSERT INTO vrps 
            (id, status, max_amount, frequency, valid_until, recipient_account)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (
                vrp_id,
                VRP_STATUSES["active"],
                request.json['max_amount'],
                request.json['frequency'],
                request.json['valid_until'],
                request.json['recipient_account']
            ),
            commit=True
        )

        if not result:
            return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), status.HTTP_500_INTERNAL_SERVER_ERROR

        cur = safe_db_query('SELECT * FROM vrps WHERE id = ?', (vrp_id,))
        return jsonify(serialize_vrp(cur.fetchone())), status.HTTP_201_CREATED

    # GET with pagination
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', PAGINATION_CONFIG["default_page_size"]))
        page = max(page, 1)
        page_size = min(page_size, PAGINATION_CONFIG["max_page_size"])
        offset = (page - 1) * page_size
    except ValueError:
        logger.warning("Invalid pagination parameters")
        return jsonify({
            "error": RESPONSE_MESSAGES["validation_error"],
            "message": "Неверные параметры пагинации"
        }), status.HTTP_400_BAD_REQUEST

    cur = safe_db_query(
        'SELECT * FROM vrps ORDER BY valid_until DESC LIMIT ? OFFSET ?',
        (page_size, offset)
    )

    return jsonify({
        "vrps": [serialize_vrp(row) for row in cur.fetchall()],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "next_page": f"?page={page + 1}&page_size={page_size}" if cur.rowcount == page_size else None
        }
    }), status.HTTP_200_OK


@vrp_bp.route('/vrp-v1.3.1/<vrp_id>', methods=['GET', 'PUT', 'DELETE'])
@swag_from('../docs/vrp.yml')
def single_vrp(vrp_id):
    logger.info(f"{request.method} {request.path} | id={vrp_id}")

    cur = safe_db_query('SELECT * FROM vrps WHERE id = ?', (vrp_id,))
    vrp = cur.fetchone() if cur else None

    if not vrp:
        return jsonify({"error": RESPONSE_MESSAGES["not_found"]}), status.HTTP_404_NOT_FOUND

    if request.method == 'PUT':
        error = safe_validate(request.json, vrp_schema)
        if error:
            return jsonify({
                "error": RESPONSE_MESSAGES["validation_error"],
                "message": error
            }), status.HTTP_400_BAD_REQUEST

        result = safe_db_query(
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

        if not result:
            return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), status.HTTP_500_INTERNAL_SERVER_ERROR

        cur = safe_db_query('SELECT * FROM vrps WHERE id = ?', (vrp_id,))
        vrp = cur.fetchone()

    elif request.method == 'DELETE':
        result = safe_db_query('DELETE FROM vrps WHERE id = ?', (vrp_id,), commit=True)
        if not result:
            return jsonify({"error": RESPONSE_MESSAGES["db_error"]}), status.HTTP_500_INTERNAL_SERVER_ERROR
        return '', status.HTTP_204_NO_CONTENT

    return jsonify(serialize_vrp(vrp)), status.HTTP_200_OK
