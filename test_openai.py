from src.llm import OpenAIProvider

llm = OpenAIProvider()

result = llm.generate(
    'Return exactly this JSON: {"status": "working"}'
)

print(result)