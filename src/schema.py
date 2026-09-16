from enum import Enum
from pydantic import BaseModel


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class AuthMethod(str, Enum):
    API_KEY = "API_KEY"
    OAUTH2 = "OAUTH2"
    BEARER_TOKEN = "BEARER_TOKEN"
    BASIC_AUTH = "BASIC_AUTH"
    PERSONAL_ACCESS_TOKEN = "PERSONAL_ACCESS_TOKEN"
    UNKNOWN = "UNKNOWN"


class APIStyle(str, Enum):
    REST = "REST"
    GRAPHQL = "GRAPHQL"
    SOAP = "SOAP"
    RPC = "RPC"
    UNKNOWN = "UNKNOWN"


class MCPClass(str, Enum):
    OFFICIAL = "OFFICIAL_MCP_EXISTS"
    COMMUNITY = "COMMUNITY_MCP_EXISTS"
    NONE = "NO_MCP_FOUND"
    UNKNOWN = "UNKNOWN"


class AccessModel(str, Enum):
    SELF_SERVE = "SELF_SERVE"
    GATED = "GATED_SALES"
    FREEMIUM = "FREEMIUM_SELF_SERVE"
    UNKNOWN = "UNKNOWN"


class WebhookSupport(str, Enum):
    YES = "YES"
    NO = "NO"
    UNKNOWN = "UNKNOWN"


class Evidence(BaseModel):
    evidence_id: str
    url: str = ""
    quote: str = ""
    title: str = ""
    source_type: str = ""
    field: str = ""


class Description(BaseModel):
    value: str
    evidence: list[Evidence]
    confidence: Confidence


class Authentication(BaseModel):
    methods: list[AuthMethod]
    evidence: list[Evidence]
    confidence: Confidence


class Access(BaseModel):
    classification: AccessModel
    evidence: list[Evidence]
    confidence: Confidence


class API(BaseModel):
    styles: list[APIStyle]
    breadth: str
    resources: list[str]
    actions: list[str]
    webhooks: WebhookSupport
    evidence: list[Evidence]
    confidence: Confidence


class MCP(BaseModel):
    classification: MCPClass
    evidence: list[Evidence]
    confidence: Confidence

class BuildabilityVerdict(str, Enum):
    READY_NOW = "READY_NOW"
    NEEDS_WORK = "NEEDS_WORK"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


class Buildability(BaseModel):
    verdict: BuildabilityVerdict = BuildabilityVerdict.UNKNOWN
    blockers: list[str]
    reasoning: str


class AppResearch(BaseModel):
    app_name: str
    category: str = "UNKNOWN"
    description: Description
    authentication: Authentication
    access_model: Access
    api: API
    mcp: MCP
    buildability: Buildability