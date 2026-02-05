import asyncio
import base64
import os
from pathlib import Path
from openai import OpenAI
from playwright.async_api import async_playwright
from pydantic import BaseModel
import dotenv
import django

dotenv.load_dotenv()

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "graph.settings")
django.setup()

from data.models import PolicyViolation
from search import search_multiple_queries
import json


class Policy(BaseModel):
    """Structured output for policy violation detection."""

    is_adderall_sold: bool
    appears_licensed_pharmacy: bool
    uses_visa: bool
    explanation: str


async def analyze_url_with_browser(
    url: str, screenshot_dir: str = "."
) -> tuple[Policy, list[str]]:
    """
    Analyze a URL using OpenAI with Playwright browser interaction tools.
    Repeatedly calls OpenAI API with tools to interact with the page until analysis is complete.
    Returns: tuple of (Policy, list of screenshot base64 strings)
    """
    client = OpenAI()
    all_screenshots = []  # Collect all screenshots

    browser_username = "brd-customer-hl_434c151b-zone-scraping_browser_dev"
    browser_password = "wbmnz4ar3xtt"
    browser_host = "brd.superproxy.io"
    browser_port = 9222

    ws_endpoint = (
        f"wss://{browser_username}:{browser_password}@{browser_host}:{browser_port}"
    )

    # Define tools for OpenAI
    tools = [
        {
            "type": "function",
            "function": {
                "name": "click",
                "description": "Click on an element on the page using a CSS selector",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS selector for the element to click",
                        }
                    },
                    "required": ["selector"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "fill",
                "description": "Fill a form field with text using a CSS selector",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS selector for the input element",
                        },
                        "value": {
                            "type": "string",
                            "description": "Text to fill in the field",
                        },
                    },
                    "required": ["selector", "value"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "browser_snapshot",
                "description": "Get a snapshot of interactive elements on the page (buttons, links, inputs)",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "take_screenshot",
                "description": "Take a screenshot of the current page state",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
    ]

    async with async_playwright() as p:
        print(f"[BROWSER] Connecting to Bright Data CDP endpoint...")
        browser = await p.chromium.connect_over_cdp(ws_endpoint)
        context = await browser.new_context()
        page = await context.new_page()

        print(f"[BROWSER] Navigating to {url}...")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        print(f"[BROWSER] Page loaded successfully")

        # Get initial page info
        title = await page.title()
        print(f"[BROWSER] Page title: {title}")

        # Initialize conversation history
        messages = [
            {
                "role": "system",
                "content": "You are analyzing a website by attempting to purchase Adderall to check if it's being sold illegally. Your goal is to navigate through the purchase flow as far as possible to gather evidence. Use the provided tools to explore the website. Search for Adderall products, add them to cart, and proceed through checkout to see payment options (especially Visa). Take screenshots at key steps (product pages, cart, checkout, payment methods). Use browser_snapshot to find interactive elements. Focus on: 1) Finding and selecting Adderall products, 2) Adding to cart, 3) Proceeding to checkout, 4) Checking if Visa is accepted as payment, 5) Looking for pharmacy licensing information. When you've gathered enough evidence or can't proceed further, stop making tool calls.",
            },
            {
                "role": "user",
                "content": f"Attempt to purchase Adderall from {url}. Navigate through the site, find Adderall products, add them to cart, and proceed through checkout to determine: 1) Is Adderall being sold? 2) Does it appear to be a licensed pharmacy? 3) Does it accept Visa payments? Take screenshots at each important step.",
            },
        ]

        screenshot_counter = 0
        max_iterations = 10

        for iteration in range(max_iterations):
            print(f"\n{'=' * 60}")
            print(f"[ITERATION {iteration + 1}/{max_iterations}]")
            print(f"{'=' * 60}")

            # Make API call with tools
            print(f"[API] Calling OpenAI with {len(messages)} messages...")
            response = client.chat.completions.create(
                model="gpt-5.2", messages=messages, tools=tools, tool_choice="auto"
            )

            assistant_message = response.choices[0].message
            print(f"[API] Response received")

            # Log assistant message content if present
            if assistant_message.content:
                print(f"[API] Assistant says: {assistant_message.content[:200]}...")

            messages.append(assistant_message)

            # Check if there are tool calls
            if not assistant_message.tool_calls:
                print(f"[API] No tool calls requested - analysis complete")
                break

            print(f"[API] {len(assistant_message.tool_calls)} tool call(s) requested")

            # Execute each tool call
            for idx, tool_call in enumerate(assistant_message.tool_calls, 1):
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                print(
                    f"\n[TOOL {idx}/{len(assistant_message.tool_calls)}] Executing: {tool_name}"
                )
                print(f"[TOOL {idx}] Arguments: {tool_args}")

                try:
                    if tool_name == "click":
                        selector = tool_args["selector"]
                        print(f"[TOOL] Clicking on selector: {selector}")
                        await page.click(selector, timeout=5000)
                        await page.wait_for_timeout(1000)  # Wait for page to update
                        current_url = page.url
                        result = f"Clicked on {selector}. Current URL: {current_url}"
                        print(f"[TOOL] ✓ Click successful. Now at: {current_url}")

                    elif tool_name == "fill":
                        selector = tool_args["selector"]
                        value = tool_args["value"]
                        print(f"[TOOL] Filling {selector} with: {value}")
                        await page.fill(selector, value, timeout=5000)
                        result = f"Filled {selector} with '{value}'"
                        print(f"[TOOL] ✓ Fill successful")

                    elif tool_name == "browser_snapshot":
                        print(
                            f"[TOOL] Getting browser snapshot of interactive elements..."
                        )
                        # Get interactive elements
                        elements = await page.evaluate("""
                            () => {
                                const els = [];
                                // Get buttons
                                document.querySelectorAll('button, a, input, select').forEach((el, idx) => {
                                    const rect = el.getBoundingClientRect();
                                    if (rect.width > 0 && rect.height > 0) {
                                        els.push({
                                            tag: el.tagName.toLowerCase(),
                                            text: el.innerText?.substring(0, 100) || el.value || el.placeholder || '',
                                            selector: el.id ? `#${el.id}` : el.className ? `.${el.className.split(' ')[0]}` : el.tagName.toLowerCase(),
                                            type: el.type || '',
                                            href: el.href || ''
                                        });
                                    }
                                });
                                return els.slice(0, 50);  // Limit to 50 elements
                            }
                        """)
                        print(f"[TOOL] ✓ Found {len(elements)} interactive elements")
                        result = json.dumps(elements, indent=2)
                        print(f"[TOOL] Sample elements: {elements[:3]}")

                    elif tool_name == "take_screenshot":
                        screenshot_counter += 1
                        screenshot_path = (
                            f"{screenshot_dir}/screenshot_{screenshot_counter}.png"
                        )
                        print(f"[TOOL] Taking full-page screenshot...")
                        await page.screenshot(path=screenshot_path, full_page=True)
                        print(f"[TOOL] ✓ Screenshot saved to {screenshot_path}")

                        # Encode screenshot for next message
                        with open(screenshot_path, "rb") as img_file:
                            image_data = base64.b64encode(img_file.read()).decode(
                                "utf-8"
                            )

                        # Store screenshot data
                        all_screenshots.append(image_data)

                        image_size_kb = len(image_data) / 1024
                        print(f"[TOOL] Screenshot encoded ({image_size_kb:.1f} KB)")

                        result = f"Screenshot saved to {screenshot_path}. Screenshot has been captured and will be included in the next message."

                except Exception as e:
                    result = f"Error: {str(e)}"
                    print(f"[TOOL] ✗ Error: {e}")

                # Add tool result to messages
                messages.append(
                    {"role": "tool", "tool_call_id": tool_call.id, "content": result}
                )

            # After all tool calls, check if we need to add screenshots
            for tool_call in assistant_message.tool_calls:
                if tool_call.function.name == "take_screenshot":
                    # Find the screenshot that was just taken
                    screenshot_path = (
                        f"{screenshot_dir}/screenshot_{screenshot_counter}.png"
                    )
                    if os.path.exists(screenshot_path):
                        print(f"[TOOL] Adding screenshot to conversation...")
                        with open(screenshot_path, "rb") as img_file:
                            image_data = base64.b64encode(img_file.read()).decode(
                                "utf-8"
                            )

                        # Add image to conversation
                        messages.append(
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Here is the screenshot you requested:",
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/png;base64,{image_data}"
                                        },
                                    },
                                ],
                            }
                        )
                        print(f"[TOOL] ✓ Screenshot added to conversation")
                        break  # Only add once per iteration

        # Final analysis call with structured output
        print(f"\n{'=' * 60}")
        print("[FINAL] Making final analysis with structured output...")
        print(f"{'=' * 60}")

        # Take final screenshot if we haven't taken any
        if screenshot_counter == 0:
            print("[FINAL] No screenshots taken yet, taking final screenshot...")
            screenshot_path = f"{screenshot_dir}/screenshot_final.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            with open(screenshot_path, "rb") as img_file:
                image_data = base64.b64encode(img_file.read()).decode("utf-8")
            all_screenshots.append(image_data)
            print(f"[FINAL] ✓ Final screenshot saved")

        print(f"[FINAL] Calling OpenAI for structured output (Policy)...")
        final_response = client.beta.chat.completions.parse(
            model="gpt-5.2",
            messages=messages
            + [
                {
                    "role": "user",
                    "content": "Based on your exploration, provide a final analysis as structured output.",
                }
            ],
            response_format=Policy,
        )

        print(f"[BROWSER] Closing browser...")
        await context.close()
        await browser.close()
        print(f"[BROWSER] ✓ Browser closed")

        result = final_response.choices[0].message.parsed
        if result is None:
            return Policy(
                is_adderall_sold=False,
                appears_licensed_pharmacy=False,
                uses_visa=False,
                explanation="Failed to parse response from OpenAI",
            ), all_screenshots

        print(f"[FINAL] ✓ Analysis complete with {len(all_screenshots)} screenshot(s)")
        return result, all_screenshots


if __name__ == "__main__":
    # Test with single URL
    TEST_MODE = False

    if TEST_MODE:
        print("=== TEST MODE: Single URL Analysis ===")
        test_url = "https://shipfromusapharmacy.com/"
        urls = [test_url]
        print(f"Testing with: {test_url}\n")
    else:
        # Get URLs from search
        print("=== Searching for Pharmacy URLs ===")
        queries = [
            "buy adderall online pharmacy",
            "adderall online no prescription",
            "order adderall pharmacy",
        ]
        urls = search_multiple_queries(queries, num_results=10, num_pages=5)
        print(f"\n=== Found {len(urls)} URLs to analyze ===\n")

    # Clear existing database entries
    # print("\n=== Clearing Database ===")
    # deleted_count = PolicyViolation.objects.all().delete()[0]
    # print(f"✓ Deleted {deleted_count} existing record(s)\n")

    # Process each URL
    for i, url in enumerate(urls, 1):
        print(f"\n{'=' * 60}")
        print(f"Processing {i}/{len(urls)}: {url}")
        print("=" * 60)

        try:
            # Analyze URL with interactive browser
            print("\n=== Analyzing with OpenAI + Browser Tools ===")
            analysis, screenshots = asyncio.run(
                analyze_url_with_browser(url, screenshot_dir=".")
            )
            print(f"Is Adderall being sold? {analysis.is_adderall_sold}")
            print(
                f"Appears to be licensed pharmacy? {analysis.appears_licensed_pharmacy}"
            )
            print(f"Uses Visa? {analysis.uses_visa}")
            print(f"Explanation: {analysis.explanation}")
            print(f"Screenshots captured: {len(screenshots)}")

            # Save to database
            print("\n=== Saving to Database ===")
            policy_violation = PolicyViolation.objects.create(
                url=url,
                title=url,  # We don't have title anymore, just use URL
                is_adderall_sold=analysis.is_adderall_sold,
                appears_licensed_pharmacy=analysis.appears_licensed_pharmacy,
                uses_visa=analysis.uses_visa,
                explanation=analysis.explanation,
                screenshot_path=f"screenshot_{i}_final.png",  # Reference final screenshot
                screenshots=screenshots,  # Store all screenshots as base64
            )
            print(f"✓ Saved to database with ID: {policy_violation.id}")
            print(f"✓ Saved {len(screenshots)} screenshot(s) to database")

        except Exception as e:
            print(f"✗ Error processing {url}: {e}")
            import traceback

            traceback.print_exc()
            continue

    print(f"\n{'=' * 60}")
    print(f"✓ Completed analysis of {len(urls)} URLs")
    print("=" * 60)

# Find a better way to scrape all websites

# Todo: create a way to navigate website
# Needs to be able to take screenshots of all pages once added to cart
# Playwright MCP would be good here
# Check false positives and negatives

# Make frontend contain more evidence

# Improvments: better guardrails would be good -
# More tools (url navigation) / better playwright MCP
# Better filtering for search
