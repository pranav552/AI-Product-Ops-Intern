from src.validator import validate_json


valid_json = """
{
  "app_name": "Notion",
  "description": {
    "value": "Test",
    "evidence": [],
    "confidence": "HIGH"
  },
  "authentication": {
    "methods": [],
    "evidence": [],
    "confidence": "HIGH"
  },
  "access_model": {
    "classification": "UNKNOWN",
    "evidence": [],
    "confidence": "HIGH"
  },
  "api": {
    "styles": [],
    "breadth": "UNKNOWN",
    "resources": [],
    "actions": [],
    "webhooks": false,
    "evidence": [],
    "confidence": "HIGH"
  },
  "mcp": {
    "classification": "UNKNOWN",
    "evidence": [],
    "confidence": "HIGH"
  },
  "buildability": {
    "blockers": [],
    "reasoning": ""
  }
}
"""

ok, data, errors = validate_json(valid_json)

print("Valid:", ok)
print("Errors:", errors)