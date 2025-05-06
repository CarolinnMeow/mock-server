from .accounts import accounts_bp
from .payments import payments_bp
from .consents import consents_bp
from .documents import documents_bp
from .vrp import vrp_bp
from .transactions import transactions_bp
from .medical import medical_bp
from .product_agreements import product_agreements_bp
from .pm_211fz import pm_211fz_bp
from .system import system_bp

__all__ = [
    "accounts_bp", "payments_bp", "consents_bp", "documents_bp", "vrp_bp",
    "transactions_bp", "medical_bp", "product_agreements_bp", "pm_211fz_bp", "system_bp"
]
