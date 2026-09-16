from urllib.parse import urlparse


def get_domain(url: str) -> str:
    return urlparse(url).netloc.lower()


def classify_source(
    url: str,
    official_domains: list[str]
) -> str:

    domain = get_domain(url)

    if any(
        domain == d or domain.endswith("." + d)
        for d in official_domains
    ):
        return "OFFICIAL_DEVELOPER_DOCS"

    if "github.com" in domain:
        return "OFFICIAL_GITHUB"

    return "THIRD_PARTY"


def rank_source(source_type: str) -> int:

    weights = {
        "OFFICIAL_API_DOCS": 5,
        "OFFICIAL_DEVELOPER_DOCS": 5,
        "OFFICIAL_HELP_DOCS": 4,
        "OFFICIAL_GITHUB": 4,
        "OFFICIAL_PRICING": 4,
        "THIRD_PARTY": 1,
        "SEARCH_RESULT": 0,
        "UNKNOWN": 0,
    }

    return weights.get(source_type, 0)