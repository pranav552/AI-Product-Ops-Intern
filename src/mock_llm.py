import json
import re

from src.llm import LLMProvider


class MockLLM(LLMProvider):

    def generate(self, prompt: str) -> str:

        match = re.search(
            r'"app_name"\s*:\s*"([^"]+)"',
            prompt
        )

        app_name = match.group(1) if match else "UNKNOWN"

        return json.dumps({
            "app_name": app_name,

            "description": {
                "value": "UNKNOWN",
                "evidence": [],
                "confidence": "UNKNOWN"
            },

            "authentication": {
                "methods": [],
                "evidence": [],
                "confidence": "UNKNOWN"
            },

            "access_model": {
                "classification": "UNKNOWN",
                "evidence": [],
                "confidence": "UNKNOWN"
            },

            "api": {
                "styles": [],
                "breadth": "UNKNOWN",
                "resources": [],
                "actions": [],
                "webhooks": False,
                "evidence": [],
                "confidence": "UNKNOWN"
            },

            "mcp": {
                "classification": "UNKNOWN",
                "evidence": [],
                "confidence": "UNKNOWN"
            },

            "buildability": {
                "blockers": [],
                "reasoning": ""
            }
        }, indent=2)