import json


EXTRACTION_PROMPT = """
You are a strict research extraction system.

Your ONLY source of truth is APP EVIDENCE below.

CRITICAL RULE:
A field may ONLY contain a value when the supplied evidence explicitly
supports that exact field. Otherwise use UNKNOWN, an empty list, or false
according to the schema.

Do NOT use general knowledge.
Do NOT infer.
Do NOT interpret unrelated text as evidence.
Do NOT reuse evidence from one field for another field.
Do NOT paraphrase a quote — copy the exact sentence from the evidence text.
If you cannot find an exact supporting sentence, do not invent one.

ALLOWED ENUM VALUES (use exactly these strings, nothing else):
authentication.methods: API_KEY, OAUTH2, BEARER_TOKEN, BASIC_AUTH, PERSONAL_ACCESS_TOKEN, UNKNOWN
access_model.classification: SELF_SERVE, GATED_SALES, FREEMIUM_SELF_SERVE, UNKNOWN
api.styles: REST, GRAPHQL, SOAP, RPC, UNKNOWN
api.webhooks: YES, NO, UNKNOWN
mcp.classification: OFFICIAL_MCP_EXISTS, COMMUNITY_MCP_EXISTS, NO_MCP_FOUND, UNKNOWN
confidence (all fields): HIGH, MEDIUM, LOW, UNKNOWN

FIELD DEFINITIONS:

1. description
Describe what the product/service is. Evidence must explicitly describe the product.

2. authentication
List ONLY actual API authentication mechanisms. Do NOT put product features,
AI capabilities, or product names here.

3. access_model
Describe ACCESS TO THE API/developer platform specifically — not consumer
product pricing. Do NOT classify "free trial of the product" as API access
unless the evidence explicitly connects it to developer/API access.

4. api
styles = REST, GraphQL, SOAP, RPC.
resources = actual API resources/endpoints/entities.
actions = actual API operations (create, read, update, delete).
breadth = ONLY a value if evidence explicitly supports it, else UNKNOWN.
webhooks = YES only when evidence explicitly documents webhook support.

5. mcp
ONLY classify MCP when evidence explicitly mentions Model Context Protocol,
an MCP server, or an official/community MCP integration. Do NOT confuse
MCP with AI agents, "Agentforce", APIs, SDKs, or automation in general.

6. buildability
blockers = concrete, evidence-supported implementation obstacles.
If none is supported, use [].

confidence:
HIGH = directly supported by strong official evidence
MEDIUM = supported but evidence is incomplete
LOW = weak/indirect evidence
UNKNOWN = insufficient evidence

Every factual value must have evidence: {"url": "...", "quote": "..."}
The quote must be copied verbatim from the supplied evidence text.

EVIDENCE-METHOD PAIRING RULE:
If you list ANY value in a "methods" or "styles" array (e.g. authentication.methods,
api.styles), you MUST include at least one evidence item in that field's "evidence"
array whose evidence_id you are citing to support it. A method/style listed with
zero supporting evidence will be discarded. Do not claim something and then leave
evidence empty — either provide the evidence_id proving it, or do not claim it.

Return ONLY valid JSON matching the supplied schema.

APP EVIDENCE:
"""


def prepare_llm_input(evidence_file: str) -> str:
    with open(evidence_file, "r", encoding="utf-8") as f:
        evidence = json.load(f)

    # Assign short IDs so the model references evidence instead of retyping URLs
    tagged = {
        "app_name": evidence["app_name"],
        "fields": {}
    }

    for field, items in evidence["fields"].items():
        tagged_items = []

        for i, item in enumerate(items):
            tagged_items.append({
                "evidence_id": f"{field[:3]}{i}",
                "url": item["url"],
                "text": item["text"][:2000],
            })

        tagged["fields"][field] = tagged_items

    instructions = EXTRACTION_PROMPT + """

EVIDENCE FORMAT CHANGE:
Each evidence item has an "evidence_id" (e.g. "aut0", "api1").
When citing evidence for any field, use this exact format:
{"evidence_id": "aut0", "quote": "<exact sentence copied from that item's text>"}

Do NOT type out the URL yourself. Use evidence_id only.
Only use evidence_id values that appear in the EVIDENCE below — never invent one.
"""

    return (
        instructions
        + "\n\nEVIDENCE:\n"
        + json.dumps(tagged, indent=2, ensure_ascii=False)
    )