from src.schema import AuthMethod, APIStyle, MCPClass, AccessModel, WebhookSupport
from src.grounding import quote_is_grounded, url_is_known_source
def _enum_value(x):
    return x.value if hasattr(x, "value") else x


AUTH_TERM_MAP = {
    "API_KEY": {"api key", "api-key"},
    "OAUTH2": {"oauth", "oauth2", "oauth 2.0"},
    "BEARER_TOKEN": {"bearer"},
    "BASIC_AUTH": {"basic authentication", "basic auth"},
    "PERSONAL_ACCESS_TOKEN": {"personal access token", "pat"},
}

API_STYLE_TERM_MAP = {
    "REST": {"rest api", "restful api"},
    "GRAPHQL": {"graphql"},
    "SOAP": {"soap"},
    "RPC": {"rpc"},
}

ACCESS_TERM_MAP = {
    "SELF_SERVE": {"self-serve", "self serve", "developer account", "sign up", "register"},
    "GATED_SALES": {"contact sales", "approval", "request access", "application required"},
    "FREEMIUM_SELF_SERVE": {"free tier", "freemium", "trial"},
}

WEBHOOK_YES_TERMS = {"webhook", "webhooks"}
WEBHOOK_NO_TERMS = {"does not support webhooks", "webhooks are not supported", "webhook is not supported"}
MCP_TERMS = {"model context protocol", "mcp server", "mcp"}


def _evidence_by_id_for_field(evidence_by_field: dict, field: str) -> dict:
    items = evidence_by_field.get(field, [])
    return {f"{field[:3]}{i}": item for i, item in enumerate(items)}


def _ground_evidence_list(
    claimed_evidence: list[dict],
    evidence_by_id: dict,
    field: str,
    log: list[str]
) -> list[dict]:
    grounded = []

    for item in claimed_evidence:
        eid = item.get("evidence_id", "")
        quote = item.get("quote", "")

        source = evidence_by_id.get(eid)

        if not source:
            log.append(
                f"{field}: dropped evidence with unknown/invented evidence_id: {eid}"
            )
            continue

        if not quote_is_grounded(quote, source.get("text", "")):
            log.append(
                f"{field}: dropped fabricated/ungrounded quote for evidence_id: {eid}"
            )
            continue

        grounded.append({
            "url": source["url"],
            "quote": quote
        })

    return grounded

def _grounded_text(grounded_evidence: list[dict]) -> str:
    return " ".join(item.get("quote", "").lower() for item in grounded_evidence)


def _contains_any(text: str, terms: set[str]) -> bool:
    return any(term in text for term in terms)


def _compute_confidence(grounded_evidence: list[dict], term_matched: bool) -> str:
    if not grounded_evidence:
        return "UNKNOWN"
    if term_matched and len(grounded_evidence) >= 1:
        return "HIGH" if len(grounded_evidence) > 1 or term_matched else "MEDIUM"
    return "LOW"


def ground_and_repair(record: dict, evidence_by_field: dict) -> tuple[dict, list[str]]:
    """
    Downgrades unsupported claims to UNKNOWN instead of failing the whole
    record. Returns the repaired record and a human-readable repair log.
    """

    log: list[str] = []

    # ---------------- description ----------------
    desc = record["description"]
    by_id = _evidence_by_id_for_field(evidence_by_field, "description")
    grounded = _ground_evidence_list(desc["evidence"], by_id, "description", log)
    desc["evidence"] = grounded
    if not grounded:
        desc["value"] = "UNKNOWN"
    desc["confidence"] = _compute_confidence(grounded, term_matched=bool(grounded))

    # ---------------- authentication ----------------
    auth = record["authentication"]
    by_id = _evidence_by_id_for_field(evidence_by_field, "authentication")
    grounded = _ground_evidence_list(auth["evidence"], by_id, "authentication", log)
    auth["evidence"] = grounded
    gtext = _grounded_text(grounded)

    kept_methods = []
    for method in auth["methods"]:
        if method == AuthMethod.UNKNOWN:
            continue
        terms = AUTH_TERM_MAP.get(_enum_value(method), set())
        if terms and _contains_any(gtext, terms):
            kept_methods.append(method)
        else:
            log.append(f"authentication: downgraded unsupported method {method} to UNKNOWN")

    auth["methods"] = kept_methods if kept_methods else [AuthMethod.UNKNOWN]
    auth["confidence"] = _compute_confidence(grounded, term_matched=bool(kept_methods))

    # ---------------- access_model ----------------
    access = record["access_model"]
    by_id = _evidence_by_id_for_field(evidence_by_field, "access_model")
    grounded = _ground_evidence_list(access["evidence"], by_id, "access_model", log)
    access["evidence"] = grounded
    gtext = _grounded_text(grounded)

    classification = access["classification"]
    if classification != AccessModel.UNKNOWN:
        terms = ACCESS_TERM_MAP.get(_enum_value(classification), set())
        if not (grounded and terms and _contains_any(gtext, terms)):
            log.append(f"access_model: downgraded unsupported classification {classification} to UNKNOWN")
            classification = AccessModel.UNKNOWN
    access["classification"] = classification
    access["confidence"] = _compute_confidence(grounded, term_matched=(classification != AccessModel.UNKNOWN))

    # ---------------- api ----------------
    api = record["api"]
    by_id = _evidence_by_id_for_field(evidence_by_field, "api")
    grounded = _ground_evidence_list(api["evidence"], by_id, "api", log)
    api["evidence"] = grounded
    gtext = _grounded_text(grounded)

    kept_styles = []
    for style in api["styles"]:
        if style == APIStyle.UNKNOWN:
            continue
        terms = API_STYLE_TERM_MAP.get(_enum_value(style), set())
        if terms and _contains_any(gtext, terms):
            kept_styles.append(style)
        else:
            log.append(f"api: downgraded unsupported style {style} to UNKNOWN")
    api["styles"] = kept_styles if kept_styles else [APIStyle.UNKNOWN]

    if not grounded:
        api["breadth"] = "UNKNOWN"
        api["resources"] = []
        api["actions"] = []

    # webhooks: silence means UNKNOWN, never NO. Explicit YES needs explicit terms.
    webhooks = api.get("webhooks", WebhookSupport.UNKNOWN)
    # separately ground webhook-specific evidence pool
    w_by_id = _evidence_by_id_for_field(evidence_by_field, "webhooks")
    w_grounded = _ground_evidence_list(
        api.get("evidence", []),
        w_by_id,
        "webhooks",
         []
    ) or grounded
    wtext = _grounded_text(w_grounded) + " " + gtext

    if webhooks == WebhookSupport.YES and not _contains_any(wtext, WEBHOOK_YES_TERMS):
        log.append("api.webhooks: downgraded unsupported YES to UNKNOWN")
        webhooks = WebhookSupport.UNKNOWN
    elif webhooks == WebhookSupport.NO and not _contains_any(wtext, WEBHOOK_NO_TERMS):
        log.append("api.webhooks: downgraded unsupported NO to UNKNOWN (absence of evidence is not evidence of absence)")
        webhooks = WebhookSupport.UNKNOWN
    api["webhooks"] = webhooks

    api["confidence"] = _compute_confidence(grounded, term_matched=bool(kept_styles))

    # ---------------- mcp ----------------
    mcp = record["mcp"]
    by_id = _evidence_by_id_for_field(evidence_by_field, "mcp")
    grounded = _ground_evidence_list(mcp["evidence"], by_id, "mcp", log)
    mcp["evidence"] = grounded
    gtext = _grounded_text(grounded)

    classification = mcp["classification"]
    if classification != MCPClass.UNKNOWN:
        if not (grounded and _contains_any(gtext, MCP_TERMS)):
            log.append(f"mcp: downgraded unsupported classification {classification} to UNKNOWN")
            classification = MCPClass.UNKNOWN
    mcp["classification"] = classification
    mcp["confidence"] = _compute_confidence(grounded, term_matched=(classification != MCPClass.UNKNOWN))

    # ---------------- buildability ----------------
    # blockers must trace back to grounded evidence somewhere in the record;
    # simplest safe rule: if no field has any grounded evidence at all,
    # buildability claims are unsupported speculation.
    any_grounded = any([
        record["description"]["evidence"],
        record["authentication"]["evidence"],
        record["access_model"]["evidence"],
        record["api"]["evidence"],
        record["mcp"]["evidence"],
    ])
    if not any_grounded and record["buildability"]["blockers"]:
        log.append("buildability: no grounded evidence anywhere in record, clearing unsupported blockers")
        record["buildability"]["blockers"] = []
        record["buildability"]["reasoning"] = "UNKNOWN"

    return record, log