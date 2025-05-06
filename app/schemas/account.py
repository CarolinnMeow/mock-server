physical_account_schema = {
    "type": "object",
    "properties": {
        "balance": {"type": "number"},
        "currency": {"type": "string"}
    },
    "required": ["balance", "currency"]
}

legal_account_schema = {
    "type": "object",
    "properties": {
        "balance": {"type": "number"},
        "currency": {"type": "string"}
    },
    "required": ["balance", "currency"]
}
