import asyncio
import base64
import httpx
from openai import OpenAI
from pathlib import Path
from playwright.async_api import async_playwright
from pydantic import BaseModel

import dotenv

dotenv.load_dotenv()
# Given a generic url: scrape website
# Check for policy violations
# Store results in DB


class Policy(BaseModel):
    """Structured output for policy violation detection."""

    is_adderall_sold: bool
    appears_licensed_pharmacy: bool
    explanation: str


def analyze_screenshot_for_adderall(screenshot_path: str) -> Policy:
    """Analyze a screenshot using OpenAI Vision API to detect if Adderall is being sold."""
    client = OpenAI()

    # Read and encode the image
    image_path = Path(screenshot_path)
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")

    # Create the API request with structured output using Responses API
    response = client.responses.parse(
        model="gpt-5.2",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Analyze this screenshot of a website. Is Adderall (or generic amphetamine/dextroamphetamine) being sold on this page? Does the website appear to be a licensed pharmacy (legitimate pharmacy with proper credentials/verification)? Provide a clear explanation of what you see.",
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{image_data}",
                    },
                ],
            }
        ],
        text_format=Policy,
    )

    result = response.output_parsed
    if result is None:
        return Policy(
            is_adderall_sold=False,
            appears_licensed_pharmacy=False,
            explanation="Failed to parse response from OpenAI",
        )

    return result


async def scrape_with_proxy(url: str) -> httpx.Response:
    """Scrape a URL using Bright Data residential proxy."""
    proxy_username = "brd-customer-hl_434c151b-zone-residential_proxy1"
    proxy_password = "k0bic2wypbfj"
    proxy_host = "brd.superproxy.io"
    proxy_port = 22225

    proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"

    async with httpx.AsyncClient(proxy=proxy_url) as client:
        response = await client.get(url, timeout=30.0)
        return response


async def test_browser_connection() -> bool:
    """Test if the Bright Data Browser API connection works."""
    browser_username = "brd-customer-hl_434c151b-zone-scraping_browser_dev"
    browser_password = "wbmnz4ar3xtt"
    browser_host = "brd.superproxy.io"
    browser_port = 9222

    ws_endpoint = (
        f"wss://{browser_username}:{browser_password}@{browser_host}:{browser_port}"
    )

    try:
        print(f"Testing connection to: {ws_endpoint.replace(browser_password, '***')}")
        async with async_playwright() as p:
            print("Connecting to browser...")
            browser = await p.chromium.connect_over_cdp(ws_endpoint)
            print("✓ Browser connected successfully!")

            context = await browser.new_context()
            page = await context.new_page()
            print("✓ Page created")

            # Test with a simple, fast-loading page
            print("Testing with example.com...")
            await page.goto("https://example.com", timeout=60000)
            print(f"✓ Page loaded: {await page.title()}")

            await context.close()
            await browser.close()
            print("✓ Connection test successful!")
            return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


async def scrape_with_browser(
    url: str, screenshot_path: str = "screenshot.png"
) -> dict:
    """Scrape a URL using Bright Data Browser API with screenshot capability."""
    browser_username = "brd-customer-hl_434c151b-zone-scraping_browser_dev"
    browser_password = "wbmnz4ar3xtt"
    browser_host = "brd.superproxy.io"
    browser_port = 9222

    # CDP endpoint for Bright Data Scraping Browser
    ws_endpoint = (
        f"wss://{browser_username}:{browser_password}@{browser_host}:{browser_port}"
    )

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(ws_endpoint)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to URL with longer timeout and better error handling
        print(f"Navigating to {url}...")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")

        # Take screenshot
        await page.screenshot(path=screenshot_path, full_page=True)

        # Get page content
        content = await page.content()
        title = await page.title()

        await context.close()
        await browser.close()

        return {
            "title": title,
            "content": content,
            "screenshot": screenshot_path,
            "url": url,
        }


if __name__ == "__main__":
    # First test the browser connection
    print("=== Testing Browser Connection ===")
    connection_ok = asyncio.run(test_browser_connection())

    if not connection_ok:
        print("\nBrowser connection failed. Check your credentials and network.")
        exit(1)

    print("\n=== Scraping Target URL ===")
    url = "https://shipfromusapharmacy.com/"

    # Option 1: Simple proxy scraping
    # response = asyncio.run(scrape_with_proxy(url))
    # print(f"Status: {response.status_code}")
    # print(f"Content length: {len(response.content)}")
    # print(response.text[:500])

    # Option 2: Browser-based scraping with screenshot
    result = asyncio.run(scrape_with_browser(url, "pharmacy_screenshot.png"))
    print(f"Title: {result['title']}")
    print(f"Screenshot saved to: {result['screenshot']}")

    print("\n=== Analyzing Screenshot with OpenAI ===")
    analysis = analyze_screenshot_for_adderall(result["screenshot"])
    print(f"Is Adderall being sold? {analysis.is_adderall_sold}")
    print(f"Explanation: {analysis.explanation}")
    print(f"Title: {result['title']}")
    print(f"Screenshot saved to: {result['screenshot']}")
    print(f"Content length: {len(result['content'])}")
