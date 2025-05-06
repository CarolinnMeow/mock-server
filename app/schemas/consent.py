consent_schema = {
    "type": "object",
    "properties": {
        "subject": {"type": "string"},
        "scope": {"type": "string"}
    },
    "required": ["subject", "scope"]
}
