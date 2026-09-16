from src.fetcher import fetch_page
from src.evidence import find_evidence

result = fetch_page("https://developers.notion.com/")

evidence = find_evidence(
    result["text"],
    ["authentication", "OAuth", "API"]
)

print("Evidence found:", len(evidence))

for item in evidence:
    print("\n--- EVIDENCE ---")
    print(item[:700])