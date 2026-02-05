import os
from serpapi import GoogleSearch
import dotenv

dotenv.load_dotenv()


def search_adderall_pharmacies(
    query: str = "buy adderall online pharmacy",
    num_results: int = 10,
    num_pages: int = 1,
) -> list[str]:
    """
    Search for pharmacies selling Adderall using Google Search via SerpAPI.
    Returns a list of URLs to investigate.

    Args:
        query: Search query string
        num_results: Number of results per page (max 100)
        num_pages: Number of pages to fetch
    """
    all_urls = []

    for page in range(num_pages):
        start = page * num_results
        print(
            f"  Fetching page {page + 1}/{num_pages} (results {start}-{start + num_results})..."
        )

        params = {
            "engine": "google",
            "q": query,
            "num": num_results,
            "start": start,  # Offset for pagination
            "api_key": os.environ["SERP_API_KEY"],
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        # Extract URLs from organic results
        if "organic_results" in results:
            for result in results["organic_results"]:
                if "link" in result:
                    all_urls.append(result["link"])

        # Extract URLs from shopping results if present
        if "shopping_results" in results:
            for result in results["shopping_results"]:
                if "link" in result:
                    all_urls.append(result["link"])

        print(
            f"  Page {page + 1}: Found {len(results.get('organic_results', []))} organic results"
        )

    return all_urls


def search_multiple_queries(
    queries: list[str], num_results: int = 10, num_pages: int = 1
) -> list[str]:
    """
    Search multiple queries and return deduplicated list of URLs.

    Args:
        queries: List of search query strings
        num_results: Number of results per page
        num_pages: Number of pages to fetch per query
    """
    all_urls = set()

    for query in queries:
        print(f"Searching: {query}")
        urls = search_adderall_pharmacies(query, num_results, num_pages)
        all_urls.update(urls)
        print(f"  Total found for '{query}': {len(urls)} URLs")

    return list(all_urls)


if __name__ == "__main__":
    # Define search queries to find suspicious pharmacies
    queries = [
        "buy adderall online pharmacy",
        "adderall online no prescription",
        "order adderall pharmacy",
    ]

    print("=== Searching for Pharmacy URLs ===\n")
    urls = search_multiple_queries(queries, num_results=10, num_pages=3)

    print(f"\n=== Found {len(urls)} unique URLs ===")
    for i, url in enumerate(urls, 1):
        print(f"{i}. {url}")

    print("\n=== URLs ready for analysis ===")
