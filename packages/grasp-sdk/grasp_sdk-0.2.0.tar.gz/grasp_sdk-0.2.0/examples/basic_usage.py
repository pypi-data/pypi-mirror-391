#!/usr/bin/env python3
"""
Basic usage example for Grasp Python SDK.

This example shows how to:
1. Create a Grasp client
2. Create a container
3. Get browser information
4. Shutdown the container
"""

import os
from grasp import Grasp


def main():
    # Initialize client (API key from environment or pass directly)
    client = Grasp(
        api_key=os.getenv("GRASP_API_KEY"),  # or api_key="your-api-key"
        base_url=os.getenv("GRASP_BASE_URL", "https://api.getgrasp.ai"),
    )

    try:
        # Create a new container with options
        print("Creating container...")
        container = client.create(
            idle_timeout=30000,  # 30 seconds idle timeout
            proxy={
                "enabled": True,
                "type": "residential",
                "country": "US",
            },
        )

        print(f"Container created: {container.id}")
        print(f"Status: {container.status}")
        print(f"Created at: {container.created_at}")
        print(f"CDP WebSocket: {container.browser.ws_endpoint}")
        print(f"Live view URL: {container.browser.live_url}")

        # You can now use the WebSocket endpoint with Playwright or Puppeteer
        # Example: browser = playwright.chromium.connect_over_cdp(container.browser.ws_endpoint)

        input("Press Enter to shutdown the container...")

        # Shutdown the container when done
        print("Shutting down container...")
        container.shutdown()
        print("Container shut down successfully")

    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()