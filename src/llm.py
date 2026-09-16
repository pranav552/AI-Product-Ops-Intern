from ollama import chat
from src.schema import AppResearch


class LLMProvider:
    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class OllamaProvider(LLMProvider):

    def __init__(self, model="llama3.2:3b"):
        self.model = model

    def generate(self, prompt: str) -> str:

        response = chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            format=AppResearch.model_json_schema(),
            options={"temperature": 0},
        )

        return response["message"]["content"]