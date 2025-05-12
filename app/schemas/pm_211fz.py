pm_211fz_schema = {
    "type": "object",
    "properties": {
        "amount": {"type": "number"},
        "currency": {"type": "string"},
        "recipient": {"type": "string"},
        "purpose": {"type": "string"},
        "budget_code": {"type": "string"},
        "account_id": {"type": "string"}
    },
    "required": ["amount", "currency", "recipient", "purpose", "budget_code", "account_id"]
}
