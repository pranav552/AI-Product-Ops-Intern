import json

from src.extractor import prepare_llm_input
from src.mock_llm import MockLLM
from src.validator import validate_json
from src.evidence_validator import validate_evidence


# 1. Prepare the real fetched evidence
prompt = prepare_llm_input(
    "data/evidence/notion_fetched.json"
)

# 2. Run the LLM layer
llm = MockLLM()
raw_output = llm.generate(prompt)

print("LLM output received.")

# 3. Validate JSON structure
json_ok, record, json_errors = validate_json(raw_output)

print("JSON valid:", json_ok)

if not json_ok:
    print("JSON errors:", json_errors)
    raise SystemExit(1)

# 4. Validate evidence grounding
evidence_errors = validate_evidence(record)

print("Evidence errors:", evidence_errors)

# 5. Save extracted record
with open(
    "data/results/notion_extracted.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        record,
        f,
        indent=2,
        ensure_ascii=False
    )

print("Saved: data/results/notion_extracted.json")