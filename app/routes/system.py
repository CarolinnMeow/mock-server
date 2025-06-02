from flask import Blueprint, jsonify, request
from flask_api import status
import logging
import psutil
import sqlite3
from datetime import datetime
from app.config import SYSTEM_CONFIG, RESPONSE_MESSAGES, ACCOUNT_TYPES
from app.db import execute_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

system_bp = Blueprint('system', __name__)


@system_bp.route('/')
def index():
    logger.info("Root endpoint accessed")
    return jsonify({
        "message": "Mock Server API",
        "version": SYSTEM_CONFIG["api_version"],
        "endpoints": SYSTEM_CONFIG["endpoints"]
    }), status.HTTP_200_OK


@system_bp.route('/simulate-errors', methods=['GET'])
def simulate_errors():
    error_code = request.args.get('code', '500')

    try:
        error_code = int(error_code)
        if error_code not in SYSTEM_CONFIG["allowed_error_codes"]:
            raise ValueError
    except ValueError:
        logger.warning(f"Invalid error code requested: {error_code}")
        return jsonify({
            "error": RESPONSE_MESSAGES["validation_error"],
            "message": f"Allowed error codes: {SYSTEM_CONFIG['allowed_error_codes']}"
        }), status.HTTP_400_BAD_REQUEST

    logger.info(f"Simulating error with code: {error_code}")
    return jsonify({
        "error": "Simulated error",
        "code": error_code
    }), error_code


@system_bp.route('/health', methods=['GET'])
def health_check():
    db_status = SYSTEM_CONFIG["health_statuses"]["db_disconnected"]
    try:
        safe_db_query('SELECT 1')
        db_status = SYSTEM_CONFIG["health_statuses"]["db_connected"]
    except sqlite3.Error as e:
        logger.error(f"Database health check failed: {str(e)}")

    logger.info(f"Health check status - DB: {db_status}")
    return jsonify({
        "status": "OK" if db_status == "connected" else "DEGRADED",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "database": db_status,
            "auth_service": SYSTEM_CONFIG["health_statuses"]["service_active"]
        }
    }), status.HTTP_200_OK


@system_bp.route('/metrics', methods=['GET'])
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

        # Memory usage
        memory_usage = f"{psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB"

        logger.info("Metrics collected successfully")
        return jsonify({
            "requests_total": transactions_count,
            "accounts": {
                "physical": physical_accounts,
                "legal": legal_accounts
            },
            "memory_usage": memory_usage
        }), status.HTTP_200_OK

    except Exception as e:
        logger.error(f"Metrics error: {str(e)}")
        return jsonify({
            "error": RESPONSE_MESSAGES["server_error"]
        }), status.HTTP_500_INTERNAL_SERVER_ERROR
