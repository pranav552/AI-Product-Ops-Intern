import difflib


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def quote_is_grounded(quote: str, source_text: str, threshold: float = 0.75) -> bool:
    """
    Deterministic check: does `quote` (claimed by the LLM) actually appear,
    exactly or near-exactly, inside `source_text` (the real fetched page)?

    This catches fabricated quotes — the LLM inventing a plausible-sounding
    sentence instead of copying a real one.
    """

    if not quote or not source_text:
        return False

    nq = _normalize(quote)
    ns = _normalize(source_text)

    if len(nq) < 8:
        return False

    if nq in ns:
        return True

    window = len(nq)
    step = max(window // 2, 20)
    best_ratio = 0.0

    for i in range(0, max(len(ns) - window, 0) + 1, step):
        chunk = ns[i:i + window + step]
        ratio = difflib.SequenceMatcher(None, nq, chunk).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
        if best_ratio >= threshold:
            break

    return best_ratio >= threshold


def url_is_known_source(url: str, known_urls: set[str]) -> bool:
    """
    Contamination check: was this URL actually fetched FOR THIS FIELD?
    If the LLM cites a URL that was never in that field's evidence pool,
    it either hallucinated the URL or leaked evidence across fields.
    """
    return url in known_urls