physical_account_schema = {
    "type": "object",
    "properties": {
        "balance": {"type": "number"},
        "currency": {"type": "string"},
        "owner": {"type": "string"},
        "status": {"type": "string"}
    },
    "required": ["balance", "currency", "owner", "status"]
}

legal_account_schema = {
    "type": "object",
    "properties": {
        "balance": {"type": "number"},
        "currency": {"type": "string"}
    },
    "required": ["balance", "currency"]
}
