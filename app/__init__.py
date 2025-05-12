from flask import Flask, g
from flasgger import Swagger
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
    return app

