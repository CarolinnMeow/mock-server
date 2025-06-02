from flask import Flask, jsonify
from flasgger import Swagger
from werkzeug.exceptions import HTTPException
import logging

from app.routes import (
    accounts_bp, payments_bp, consents_bp, documents_bp, vrp_bp,
    transactions_bp, medical_bp, product_agreements_bp, pm_211fz_bp, system_bp
)
from app.db import init_app
from app.services.data_service import DataService

def create_app(config_class=None):
    app = Flask(__name__)
    if config_class is None:
        from app.config import Config
        config_class = Config
    app.config.from_object(config_class)
    Swagger(app)
    init_app(app)

    # Регистрация blueprint'ов
    app.register_blueprint(accounts_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(consents_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(vrp_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(medical_bp)
    app.register_blueprint(product_agreements_bp)
    app.register_blueprint(pm_211fz_bp)
    app.register_blueprint(system_bp)

    # === Настройка логирования ===
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    logger = logging.getLogger(__name__)

    # === Глобальные обработчики ошибок ===

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        response = e.get_response()
        response.data = jsonify({
            "error": e.name,
            "message": e.description,
            "status": e.code
        }).data
        response.content_type = "application/json"
        logger.warning(f"HTTPException: {e.code} {e.name} - {e.description}")
        return response, e.code

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        logger.exception(f"Unhandled Exception: {str(e)}")
        response = {
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please contact support.",
            "status": 500
        }
        return jsonify(response), 500

    return app
