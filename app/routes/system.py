from flask import Blueprint, jsonify, request, abort
from datetime import datetime
import psutil
from app.services.data_service import data_service

system_bp = Blueprint('system', __name__)

@system_bp.route('/simulate-errors', methods=['GET'])
def simulate_errors():
    error_code = request.args.get('code', '500')
    abort(int(error_code))

@system_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "OK",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "database": "connected",
            "auth_service": "active"
        }
    })

@system_bp.route('/metrics', methods=['GET'])
def metrics():
    return jsonify({
        "requests_total": len(data_service.get_transactions()),
        "accounts": {
            "physical": len([a for a in data_service.get_accounts('physical_entity')]),
            "legal": len([a for a in data_service.get_accounts('legal_entity')])
        },
        "memory_usage": f"{psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB"
    })
