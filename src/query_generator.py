def generate_queries(app_name: str) -> dict[str, str]:

    return {
        "authentication": (
            f"{app_name} API authentication OAuth API key"
        ),

        "access": (
            f"{app_name} API getting started credentials developer access"
        ),

        "api": (
            f"{app_name} API reference REST GraphQL endpoints"
        ),

        "webhooks": (
            f"{app_name} API webhooks developer documentation"
        ),

        "mcp": (
            f"{app_name} MCP official Model Context Protocol"
        ),

        "pricing_access": (
            f"{app_name} API pricing developer access restrictions"
        ),
    }