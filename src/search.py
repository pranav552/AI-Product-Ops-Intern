from ddgs import DDGS
import time


def search_web(
    query: str,
    max_results: int = 5,
    domain: str | None = None
):

    search_query = query

    if domain:
        search_query = f"{query} site:{domain}"

    for attempt in range(2):

        try:

            with DDGS() as ddgs:

                results = ddgs.text(
                    search_query,
                    max_results=max_results
                )

            if results:
                return results

        except Exception as e:

            print(
                f"Search attempt {attempt + 1} failed: {e}"
            )

        time.sleep(1)

    print(f"SEARCH_FAILED: {search_query}")

    return []