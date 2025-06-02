import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class Config:
    DATABASE = os.path.join(BASE_DIR, 'data', 'mockserver.db')
    TESTING = False

class TestConfig(Config):
    DATABASE = os.path.join(BASE_DIR, 'data', 'test_mockserver.db')
    TESTING = True

# HTTP методы
HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE']

SYSTEM_CONFIG = {
    "api_version": "1.0.0",
    "allowed_error_codes": [400, 401, 403, 404, 500, 502, 503],
    "endpoints": {
        "accounts (physical)": "/accounts-v1.3.3/",
        "accounts (legal)": "/accounts-le-v2.0.0/",
        "payments": "/payments-v1.3.1/",
        "pm_211fz": "/pm-211fz-v1.3.1/",
        "consents (physical)": "/consent-pe-v2.0.0/",
        "consents (legal)": "/consent-le-v2.0.0/",
        "documents (bank)": "/bank-doc-v1.0.1/",
        "documents (insurance)": "/insurance-doc-v1.0.1/",
        "vrp": "/vrp-v1.3.1/",
        "transactions": "/transaction-history-v1.0.0/",
        "medical insured": "/medical-insured-person-v3.0.3/",
        "product agreements": "/product-agreement-consents-v1.0.1/",
        "metrics": "/metrics",
        "health": "/health"
    },
    "health_statuses": {
        "db_connected": "connected",
        "db_disconnected": "disconnected",
        "service_active": "active"
    }
}

ACCOUNT_TYPES = {
    "physical": "physical_entity",
    "legal": "legal_entity"
}

# Сообщения для ответов
RESPONSE_MESSAGES = {
    "validation_error": "Validation error",
    "server_error": "Internal server error",
    "db_error": "Database error",
    "not_found": "Not found",
    "method_not_allowed": "Method not allowed"
}

CONSENT_TYPES = {
    "physical": "physical_entity",
    "legal": "legal_entity"
}

DOCUMENT_TYPES = {
    "bank": "bank_doc",
    "insurance": "insurance_doc"
}

# Ограничения (опционально)
DOCUMENT_LIMITS = {
    "max_content_length": 10000,  # символов
    "allowed_types": ["pdf", "docx", "txt"]
}

MEDICAL_LIMITS = {
    "max_name_length": 100,  # пример ограничения
    "max_policy_length": 20
}

PAYMENT_STATUSES = {
    "pending": "PENDING",
    "completed": "COMPLETED",
    "failed": "FAILED"
}

PAYMENT_TYPES = {
    "pm_211fz": "pm_211fz",
    "standard": "standard"
}

AGREEMENT_STATUSES = {
    "active": "ACTIVE",
    "inactive": "INACTIVE",
    "pending": "PENDING"
}

PAGINATION_CONFIG = {
    "default_page_size": 50,
    "max_page_size": 100
}

VRP_STATUSES = {
    "active": "ACTIVE",
    "paused": "PAUSED",
    "expired": "EXPIRED"
}

