import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class Config:
    DATABASE = os.path.join(BASE_DIR, 'data', 'mockserver.db')
    TESTING = False

class TestConfig(Config):
    DATABASE = os.path.join(BASE_DIR, 'data', 'test_mockserver.db')
    TESTING = True

# HTTP методы и коды статусов
HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE']
HTTP_STATUS_CODES = {
    "OK": 200,
    "CREATED": 201,
    "BAD_REQUEST": 400,
    "NOT_FOUND": 404,
    "METHOD_NOT_ALLOWED": 405,
    "INTERNAL_SERVER_ERROR": 500,
    "NO_CONTENT": 204
}

# Системные настройки
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

# Типы аккаунтов
ACCOUNT_TYPES = {
    "physical": "physical_entity",
    "legal": "legal_entity"
}

# Типы согласий
CONSENT_TYPES = {
    "physical": "physical_entity",
    "legal": "legal_entity"
}

# Типы документов
DOCUMENT_TYPES = {
    "bank": "bank_doc",
    "insurance": "insurance_doc"
}

# Ограничения на документы
DOCUMENT_LIMITS = {
    "max_content_length": 10000,
    "allowed_types": ["pdf", "docx", "txt"]
}

# Ограничения на медицинские данные
MEDICAL_LIMITS = {
    "max_name_length": 100,
    "max_policy_length": 20
}

# Статусы платежей и типы
PAYMENT_STATUSES = {
    "pending": "PENDING",
    "completed": "COMPLETED",
    "failed": "FAILED"
}
PAYMENT_TYPES = {
    "pm_211fz": "pm_211fz",
    "standard": "standard"
}

# Статусы соглашений
AGREEMENT_STATUSES = {
    "active": "ACTIVE",
    "inactive": "INACTIVE",
    "pending": "PENDING"
}

# Пагинация
PAGINATION_CONFIG = {
    "default_page_size": 50,
    "max_page_size": 100
}

# Статусы VRP
VRP_STATUSES = {
    "active": "ACTIVE",
    "paused": "PAUSED",
    "expired": "EXPIRED"
}

# Сообщения для ответов
RESPONSE_MESSAGES = {
    "validation_error": "Validation error",
    "server_error": "Internal server error",
    "db_error": "Database error",
    "not_found": "Not found",
    "method_not_allowed": "Method not allowed"
}

# ====== ТЕСТОВЫЕ ДАННЫЕ ======

TEST_ACCOUNTS = {
    "physical": [
        {"balance": 1000, "currency": "RUB", "owner": "Иван Иванов", "status": "active"},
        {"balance": 200, "currency": "USD", "owner": "John Doe", "status": "blocked"},
    ],
    "legal": [
        {"balance": 5000, "currency": "RUB", "company": "ООО Ромашка", "status": "active"},
        {"balance": 300, "currency": "USD", "company": "Acme Corp", "status": "closed"},
    ]
}

TEST_CONSENTS = [
    {
        "type": "physical_entity",
        "status": "ACTIVE",
        "tpp_id": "tpp1",
        "subject": "smth",
        "scope": "smth1",
        "permissions": ["read", "write"],
        "account_id": "test-acc-1"
    },
    {
        "type": "legal_entity",
        "status": "ACTIVE",
        "tpp_id": "tpp2",
        "subject": "smth3",
        "scope": "smth2",
        "permissions": ["read"],
        "account_id": "test-acc-2"
    }
]

TEST_PAYMENTS = [
    {
        "amount": 100,
        "currency": "RUB",
        "recipient": "Иван",
        "account_id": "test-acc-1"
    },
    {
        "amount": 250,
        "currency": "USD",
        "recipient": "John",
        "account_id": "test-acc-2"
    }
]

TEST_BANK_DOCS = [
    {
        "type": "STATEMENT",
        "content": "dGVzdA==",
        "signature": "sig123",
        "account_id": "test-acc-1"
    }
]

TEST_INSURANCE_DOCS = [
    {
        "type": "POLICY",
        "content": "dGVzdA==",
        "policy_number": "P12345",
        "signature": "sig123",
        "valid_until": "2025-12-31"
    }
]

TEST_PRODUCT_AGREEMENTS = [
    {
        "product_type": "LOAN",
        "terms": {"rate": 0.15, "duration": 12},
        "account_id": "test-acc-1"
    }
]

TEST_VRPS = [
    {
        "max_amount": 5000,
        "frequency": "MONTHLY",
        "valid_until": "2026-01-01",
        "recipient_account": "RU0012345678"
    }
]

TEST_TRANSACTIONS = [
    {
        "id": "tx1",
        "amount": 100,
        "currency": "RUB",
        "date": "2025-01-01T10:00:00",
        "account_id": "test-acc-1",
        "status": "SUCCESS"
    },
    {
        "id": "tx2",
        "amount": 250,
        "currency": "USD",
        "date": "2025-01-02T12:00:00",
        "account_id": "test-acc-2",
        "status": "SUCCESS"
    }
]

TEST_MEDICAL_INSURED = [
    {
        "name": "Иван Иванов",
        "policy_number": "POL123456",
        "birth_date": "1990-01-01"
    }
]
