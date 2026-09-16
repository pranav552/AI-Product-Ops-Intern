from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
EVIDENCE_DIR = DATA_DIR / "evidence"
RESULTS_DIR = DATA_DIR / "results"
AUDITS_DIR = DATA_DIR / "audits"


MAX_SEARCH_RESULTS_PER_QUERY = 5
MAX_RESEARCH_RETRIES = 2


SOURCE_WEIGHTS = {
    "OFFICIAL_API_DOCS": 5,
    "OFFICIAL_DEVELOPER_DOCS": 5,
    "OFFICIAL_HELP_DOCS": 4,
    "OFFICIAL_GITHUB": 4,
    "OFFICIAL_PRICING": 4,
    "THIRD_PARTY": 1,
    "SEARCH_RESULT": 0,
    "UNKNOWN": 0,
}