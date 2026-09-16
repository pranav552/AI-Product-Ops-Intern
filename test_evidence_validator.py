from src.evidence_validator import validate_evidence


record = {
    "description": {
        "value": "Notion provides a REST API.",
        "evidence": [
            {
                "url": "https://developers.notion.com/",
                "quote": "With the REST API..."
            }
        ]
    },
    "authentication": {
        "methods": [],
        "evidence": []
    },
    "access_model": {
        "classification": "UNKNOWN",
        "evidence": []
    },
    "api": {
        "styles": [],
        "resources": [],
        "actions": [],
        "webhooks": False,
        "evidence": []
    },
    "mcp": {
        "classification": "UNKNOWN",
        "evidence": []
    }
}


errors = validate_evidence(record)

print("Errors:", errors)