from src.llm import OllamaProvider

llm = OllamaProvider()

result = llm.generate(
    'Return exactly this JSON: {"status": "working"}'
)

print(result)