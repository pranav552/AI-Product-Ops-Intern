import json
from pathlib import Path

from src.fetcher import fetch_page, fetch_page_rendered


MIN_TEXT_LENGTH = 200

GARBAGE_MARKERS = [
    "loading",
    "css error",
    "please refresh",
    "enable javascript",
    "please wait",
    "sorry to interrupt",
]


def is_low_quality_text(text: str, title: str) -> bool:

    stripped = text.strip()

    if len(stripped) < MIN_TEXT_LENGTH:
        return True

    lowered = stripped.lower()
    if len(stripped) < 400 and any(marker in lowered for marker in GARBAGE_MARKERS):
        return True

    if title and stripped == title.strip():
        return True

    return False


def build_evidence(discovery_file: str):

    with open(discovery_file, "r", encoding="utf-8") as f:
        discovery = json.load(f)

    output = {"app_name": discovery["app_name"], "fields": {}}

    for field, sources in discovery.get("sources", {}).items():

        field_results = []

        for source in sources[:3]:

            url = source.get("url") or source.get("href")
            if not url:
                print(f"Skipping source without URL for field: {field}")
                continue

            print(f"Fetching [{field}]: {url}")

            try:
                result = fetch_page(url)
            except Exception as e:
                print(f"Fetch failed: {url} -> {e}")
                continue

            if not result.get("success", False):
                print(f"Fetch unsuccessful: {url}")
                continue

            text = result.get("text", "")
            if not text.strip():
                continue

            if is_low_quality_text(text, source.get("title", "")):
                print(f"Rejected low-quality/SPA-shell content: {url}")
                continue

            field_results.append({
                "url": url,
                "title": source.get("title", ""),
                "source_type": source.get("source_type", "web"),
                "source_score": source.get("source_score", 0),
                "field": field,
                "text": text,
            })

        output["fields"][field] = field_results

    return output


def save_evidence(result):
    path = Path("data/evidence")
    path.mkdir(parents=True, exist_ok=True)
    file_path = path / (result["app_name"].lower().replace(" ", "_") + "_fetched.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    return file_path