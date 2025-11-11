#!/usr/bin/env python3
"""
Playwright integration example for Grasp Python SDK.

This example shows how to:
1. Create a Grasp container
2. Connect Playwright to the container
3. Perform browser automation
4. Clean up resources

Requirements:
    pip install grasp-sdk playwright
    playwright install chromium
"""

import os
from grasp import Grasp
from playwright.sync_api import sync_playwright


def main():
    # Initialize Grasp client
    grasp_client = Grasp(
        api_key=os.getenv("GRASP_API_KEY"),
        base_url=os.getenv("GRASP_BASE_URL", "https://api.getgrasp.ai"),
    )

    # Create container
    print("Creating Grasp container...")
    container = grasp_client.create(idle_timeout=60000)  # 60 seconds
    print(f"Container created: {container.id}")
    print(f"CDP endpoint: {container.browser.ws_endpoint}")
    print(f"Live view: {container.browser.live_url}")

    try:
        # Connect Playwright to the container
        with sync_playwright() as playwright:
            print("\nConnecting Playwright to container...")
            browser = playwright.chromium.connect_over_cdp(
                container.browser.ws_endpoint
            )

            # Create a new page
            page = browser.new_page()

            # Navigate to a website
            print("Navigating to example.com...")
            page.goto("https://example.com")

            # Get page title
            title = page.title()
            print(f"Page title: {title}")

            # Take screenshot
            screenshot_path = "example_screenshot.png"
            page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to: {screenshot_path}")

            # Extract text content
            content = page.text_content("body")
            print(f"Page content (first 200 chars): {content[:200]}...")

            # Perform more complex automation
            print("\nSearching on DuckDuckGo...")
            page.goto("https://duckduckgo.com")
            page.fill('input[name="q"]', "Grasp browser automation")
            page.press('input[name="q"]', "Enter")
            page.wait_for_load_state("networkidle")

            # Get search results
            results = page.query_selector_all(".result")
            print(f"Found {len(results)} search results")

            # Close browser
            browser.close()
            print("\nPlaywright browser closed")

    finally:
        # Always cleanup the container
        print("\nShutting down container...")
        container.shutdown()
        print("Container shut down successfully")


if __name__ == "__main__":
    main()