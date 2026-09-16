from src.evidence_pipeline import build_evidence, save_evidence

result = build_evidence(
    "data/evidence/notion.json"
)

path = save_evidence(result)

print("Saved:", path)

for field, sources in result["fields"].items():
    print(field, ":", len(sources), "sources fetched")