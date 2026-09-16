from src.mock_llm import MockLLM

llm = MockLLM()

result = llm.generate("test")

print(result)