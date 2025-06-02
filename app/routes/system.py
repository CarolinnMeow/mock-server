from flask import Blueprint, jsonify, request
import logging
import psutil
import sqlite3
from datetime import datetime
from app.config import (
    SYSTEM_CONFIG,
    RESPONSE_MESSAGES,
    ACCOUNT_TYPES,
    HTTP_STATUS_CODES,
    HTTP_METHODS
)
from app.db import safe_db_query
from app.utils import log_endpoint, require_headers_and_echo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

system_bp = Blueprint('system', __name__)


@system_bp.route('/')
@log_endpoint
def index():
    return jsonify({
        "message": "Mock Server API",
        "version": SYSTEM_CONFIG["api_version"],
        "endpoints": SYSTEM_CONFIG["endpoints"]
    }), HTTP_STATUS_CODES["OK"]


@system_bp.route('/simulate-errors', methods=HTTP_METHODS[:1])  # GET
@log_endpoint
def simulate_errors():
    error_code = request.args.get('code', '500')

    try:
        error_code = int(error_code)
        if error_code not in SYSTEM_CONFIG["allowed_error_codes"]:
            raise ValueError
    except ValueError:
        return jsonify({
            "error": RESPONSE_MESSAGES["validation_error"],
            "message": f"Allowed error codes: {SYSTEM_CONFIG['allowed_error_codes']}"
        }), HTTP_STATUS_CODES["BAD_REQUEST"]

    return jsonify({
        "error": "Simulated error",
        "code": error_code
    }), error_code


@system_bp.route('/health', methods=HTTP_METHODS[:1])  # GET
@log_endpoint
def health_check():
    db_status = SYSTEM_CONFIG["health_statuses"]["db_disconnected"]
    try:
        safe_db_query('SELECT 1')
        db_status = SYSTEM_CONFIG["health_statuses"]["db_connected"]
    except sqlite3.Error as e:
        logger.error(f"Database health check failed: {str(e)}")

    return jsonify({
        "status": "OK" if db_status == "connected" else "DEGRADED",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "database": db_status,
            "auth_service": SYSTEM_CONFIG["health_statuses"]["service_active"]
        }
    }), HTTP_STATUS_CODES["OK"]


@system_bp.route('/metrics', methods=HTTP_METHODS[:1])  # GET
@log_endpoint
def metrics():
    try:
        # Transactions count
        transactions = safe_db_query('SELECT COUNT(*) FROM transactions')
        transactions_count = transactions.fetchone()[0] if transactions else 0

        # Physical accounts
        physical = safe_db_query(
            'SELECT COUNT(*) FROM accounts WHERE type = ?',
            (ACCOUNT_TYPES["physical"],)
        )
        physical_accounts = physical.fetchone()[0] if physical else 0

        # Legal accounts
        legal = safe_db_query(
            'SELECT COUNT(*) FROM accounts WHERE type = ?',
            (ACCOUNT_TYPES["legal"],)
        )
        legal_accounts = legal.fetchone()[0] if legal else 0

        return jsonify({
            "requests_total": transactions_count,
            "accounts": {
                "physical": physical_accounts,
                "legal": legal_accounts
            },
            "memory_usage": f"{psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB"
        }), HTTP_STATUS_CODES["OK"]

    except Exception as e:
        logger.error(f"Metrics error: {str(e)}")
        return jsonify({
            "error": RESPONSE_MESSAGES["server_error"]
        }), HTTP_STATUS_CODES["INTERNAL_SERVER_ERROR"]
