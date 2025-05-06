payment_schema = {
    "type": "object",
    "properties": {
        "amount": {"type": "number", "minimum": 0.01},
        "currency": {"enum": ["RUB", "USD", "EUR"]},
        "recipient": {"type": "string"}
    },
    "required": ["amount", "currency", "recipient"]
}
