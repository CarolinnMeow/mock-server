bank_doc_schema = {
    "type": "object",
    "properties": {
        "content": {"type": "string"},
        "signature": {"type": "string"}
    },
    "required": ["content", "signature"]
}

insurance_doc_schema = {
    "type": "object",
    "properties": {
        "content": {"type": "string"},
        "policy_number": {"type": "string"},
        "valid_until": {"type": "string"}
    },
    "required": ["content", "policy_number", "valid_until"]
}
