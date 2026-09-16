import json
from pathlib import Path
from urllib.parse import urlparse

from src.search import search_web


FIELD_QUERIES = {

    "description": [
        "{app} official product overview",
        "{app} platform overview",
    ],

    "authentication": [
        "{app} API authentication OAuth",
        "{app} API authentication access token",
        "{app} developer OAuth API",
    ],

    "access": [
        "{app} API access pricing",
        "{app} API availability developer access",
        "{app} API editions access",
    ],

    "api": [
        "{app} REST API reference",
        "{app} API reference endpoints resources",
        "{app} developer API documentation",
    ],

    "webhooks": [
        "{app} API webhooks events",
        "{app} developer webhooks",
        "{app} webhook documentation",
    ],

    "mcp": [
        "{app} official MCP Model Context Protocol",
        "{app} official MCP server",
        "{app} developer MCP",
    ],
}


def normalize_domain(domain: str) -> str:

    domain = (
        domain
        .lower()
        .replace("https://", "")
        .replace("http://", "")
        .replace("www.", "")
        .strip("/")
    )

    return domain


def get_hostname(url: str) -> str:

    try:
        return (
            urlparse(url).hostname
            or ""
        ).lower().replace("www.", "")

    except Exception:
        return ""


def is_official_url(
    url: str,
    official_domain: str
) -> bool:

    host = get_hostname(url)

    official = normalize_domain(
        official_domain
    )

    return (
        host == official
        or host.endswith("." + official)
    )


def classify_source(
    url: str,
    official_domain: str,
    field: str
) -> str:

    host = get_hostname(url)

    official = normalize_domain(
        official_domain
    )

    if (
        host == official
        or host.endswith("." + official)
    ):

        if (
            "developer." in host
            or "docs." in host
            or "/docs/" in url.lower()
        ):
            return "OFFICIAL_DEVELOPER_DOCS"

        return "OFFICIAL"

    # MCP can legitimately exist outside the official domain.
    if field == "mcp":

        if "github.com" in host:
            return "COMMUNITY_GITHUB"

        if "modelcontextprotocol.io" in host:
            return "MCP_REGISTRY"

    return "THIRD_PARTY"


def score_result(
    result: dict,
    field: str,
    official_domain: str
) -> int:

    url = (
        result.get("href")
        or result.get("url")
        or ""
    ).lower()

    title = (
        result.get("title")
        or ""
    ).lower()

    body = (
        result.get("body")
        or ""
    ).lower()

    score = 0

    # ========================================================
    # OFFICIAL DOMAIN
    # ========================================================

    if is_official_url(
        url,
        official_domain
    ):
        score += 50

    else:

        # Non-official sources should normally not win.
        if field != "mcp":
            score -= 30

    # ========================================================
    # DEVELOPER / DOCUMENTATION SIGNALS
    # ========================================================

    if "developer." in url:
        score += 20

    if "docs." in url:
        score += 15

    if "/docs/" in url:
        score += 15

    if "reference" in url:
        score += 12

    if "api" in url:
        score += 8

    if "developers" in url:
        score += 10

    # ========================================================
    # FIELD-SPECIFIC SIGNALS
    # ========================================================

    field_terms = {

        "authentication": [
            "oauth",
            "authentication",
            "authorization",
            "access token",
            "api key",
        ],

        "access": [
            "pricing",
            "edition",
            "api access",
            "availability",
            "plan",
        ],

        "api": [
            "rest",
            "graphql",
            "soap",
            "api reference",
            "endpoint",
            "resource",
        ],

        "webhooks": [
            "webhook",
            "webhooks",
            "event",
        ],

        "mcp": [
            "mcp",
            "model context protocol",
            "mcp server",
        ],

        "description": [
            "platform",
            "product",
            "overview",
        ],
    }

    for term in field_terms.get(
        field,
        []
    ):

        if term in title:
            score += 10

        if term in body:
            score += 3

    # ========================================================
    # BAD SOURCE SIGNALS
    # ========================================================

    bad_terms = [
        "news",
        "press-release",
        "community",
        "reddit",
        "stackoverflow",
        "marketing",
    ]

    for term in bad_terms:

        if term in url:
            score -= 10

    if "blog" in url:
        score -= 5

    # ========================================================
    # SOURCE CLASS
    # ========================================================

    source_type = classify_source(
        url,
        official_domain,
        field
    )

    if source_type == "OFFICIAL_DEVELOPER_DOCS":
        score += 20

    elif source_type == "OFFICIAL":
        score += 10

    elif source_type == "THIRD_PARTY":
        score -= 10

    return score


def normalize_result(
    result: dict,
    field: str,
    official_domain: str
) -> dict:

    url = (
        result.get("href")
        or result.get("url")
        or ""
    )

    source_type = classify_source(
        url,
        official_domain,
        field
    )

    return {

        "title": result.get(
            "title",
            ""
        ),

        "url": url,

        "snippet": result.get(
            "body",
            ""
        ),

        "source_type": source_type,

        "source_score": score_result(
            result,
            field,
            official_domain
        ),

        "field": field,

        "official": is_official_url(
            url,
            official_domain
        )
    }


def discover_app(
    app_name: str,
    official_domain: str
):

    discovery = {

        "app_name": app_name,

        "official_domain":
            normalize_domain(
                official_domain
            ),

        "sources": {}
    }

    for field, templates in FIELD_QUERIES.items():

        candidates = []

        seen_urls = set()

        for template in templates:

            query = template.format(
                app=app_name
            )

            print(
                f"Searching [{field}]: {query}"
            )

            # =================================================
            # FIRST: OFFICIAL DOMAIN SEARCH
            # =================================================

            results = search_web(
                query,
                max_results=5,
                domain=official_domain
            )

            # =================================================
            # FALLBACK: GENERAL SEARCH
            # =================================================

            if not results:

                results = search_web(
                    query,
                    max_results=5
                )

            for result in results:

                normalized = normalize_result(
                    result,
                    field,
                    official_domain
                )

                url = normalized["url"]

                if not url:
                    continue

                if url in seen_urls:
                    continue

                seen_urls.add(url)

                candidates.append(
                    normalized
                )

        candidates.sort(
            key=lambda x: x[
                "source_score"
            ],
            reverse=True
        )

        discovery["sources"][field] = (
            candidates[:8]
        )

    return discovery


def save_discovery(discovery):

    Path(
        "data/evidence"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    path = (
        Path("data/evidence")
        / (
            discovery["app_name"]
            .lower()
            .replace(" ", "_")
            + ".json"
        )
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            discovery,
            f,
            indent=2,
            ensure_ascii=False
        )

    return path