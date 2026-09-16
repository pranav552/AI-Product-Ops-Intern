import json
from pathlib import Path

from src.discovery import discover_app, save_discovery
from src.evidence_pipeline import build_evidence, save_evidence
from src.extractor import prepare_llm_input
from src.llm import OllamaProvider
from src.validator import validate_json
from src.evidence_validator import ground_and_repair


def save_result(result: dict, app_name: str):
    path = Path("data/results")
    path.mkdir(parents=True, exist_ok=True)
    file_path = path / (app_name.lower().replace(" ", "_") + ".json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    return file_path


def save_repair_log(log: list[str], app_name: str):
    path = Path("data/results")
    path.mkdir(parents=True, exist_ok=True)
    file_path = path / (app_name.lower().replace(" ", "_") + "_repair_log.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({"app_name": app_name, "repairs": log}, f, indent=2, ensure_ascii=False)
    return file_path


def run_app(app_name: str, website: str):

    print()
    print("=" * 60)
    print(f"Processing: {app_name}")
    print(f"Website: {website}")
    print("=" * 60)

    # STEP 1 — DISCOVERY
    discovery = discover_app(app_name, website)
    discovery_path = save_discovery(discovery)
    print(f"Discovery: {discovery_path}")

    # STEP 2 — FETCH EVIDENCE
    evidence = build_evidence(str(discovery_path))
    evidence_path = save_evidence(evidence)
    print(f"Evidence: {evidence_path}")

    # STEP 3 — LLM EXTRACTION (schema-locked, real prompt)
    prompt = prepare_llm_input(str(evidence_path))
    llm = OllamaProvider()
    raw_output = llm.generate(prompt)
    print("\nLLM output received.")

    # STEP 4 — STRUCTURAL VALIDATION (hard stop if this fails — not parseable)
    valid, data, errors = validate_json(raw_output)
    if not valid:
        print("JSON/schema validation FAILED (hard stop — not repairable)")
        print(errors)
        return None
    print("JSON/schema validation PASSED")

    # STEP 5 — GROUNDING & REPAIR (never hard-fails; downgrades instead)
    repaired_data, repair_log = ground_and_repair(data, evidence["fields"])

    if repair_log:
        print(f"\nGrounding repairs applied ({len(repair_log)}):")
        for line in repair_log:
            print(f"  - {line}")
    else:
        print("\nNo repairs needed — every claim was already grounded.")

    # STEP 6 — SAVE
    result_path = save_result(repaired_data, app_name)
    repair_log_path = save_repair_log(repair_log, app_name)
    print(f"\nFINAL RESULT: {result_path}")
    print(f"REPAIR LOG:   {repair_log_path}")

    return repaired_data