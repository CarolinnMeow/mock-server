product_agreement_schema = {
    "type": "object",
    "properties": {
        "product_type": {"enum": ["LOAN", "DEPOSIT", "INSURANCE"]},
        "terms": {"type": "object"}
    },
    "required": ["product_type", "terms"]
}
