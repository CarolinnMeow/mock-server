medical_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "policy_number": {"type": "string"},
        "birth_date": {"type": "string", "format": "date"}
    },
    "required": ["name", "policy_number"]
}
