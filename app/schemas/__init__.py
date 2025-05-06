from .account import physical_account_schema, legal_account_schema
from .payment import payment_schema
from .consent import consent_schema
from .document import bank_doc_schema, insurance_doc_schema
from .vrp import vrp_schema
from .medical import medical_schema
from .product_agreement import product_agreement_schema
from .pm_211fz import pm_211fz_schema

__all__ = [
    "physical_account_schema", "legal_account_schema", "payment_schema", "consent_schema",
    "bank_doc_schema", "insurance_doc_schema", "vrp_schema", "medical_schema",
    "product_agreement_schema", "pm_211fz_schema"
]
