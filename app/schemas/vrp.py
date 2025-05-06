vrp_schema = {
    "type": "object",
    "properties": {
        "max_amount": {"type": "number", "minimum": 1},
        "frequency": {"enum": ["DAILY", "WEEKLY", "MONTHLY"]},
        "valid_until": {"type": "string", "format": "date"},
        "recipient_account": {"type": "string", "pattern": "^[A-Z]{2}\\d{2}[A-Z0-9]{1,30}$"}
    },
    "required": ["max_amount", "frequency", "valid_until", "recipient_account"]
}
