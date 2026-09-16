from src.fetcher import fetch_page

url = "https://developers.notion.com/"

result = fetch_page(url)

print("Success:", result["success"])
print("Status:", result["status_code"])
print("Characters:", len(result["text"]))
print(result["text"][:1000])