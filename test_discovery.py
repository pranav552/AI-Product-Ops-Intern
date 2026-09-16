from src.discovery import discover_app, save_discovery

result = discover_app(
    "Notion",
    ["notion.com"]
)

path = save_discovery(result)

print("Saved:", path)