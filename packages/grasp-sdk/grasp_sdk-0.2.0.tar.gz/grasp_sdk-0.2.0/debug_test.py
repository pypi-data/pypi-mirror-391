#!/usr/bin/env python3
"""Debug script to understand why containers are being created multiple times."""

import os
import asyncio
import sys
import traceback

# Set test environment
os.environ["GRASP_API_KEY"] = "api-server-test"
os.environ["GRASP_BASE_URL"] = "http://localhost:3000"

# Add src to path
sys.path.insert(0, "src")

from grasp import AsyncGrasp

async def test_single_container():
    """Test creating a single container with detailed logging."""
    print("=" * 50)
    print("Starting single container test")
    print("=" * 50)

    grasp = AsyncGrasp(
        api_key=os.environ["GRASP_API_KEY"],
        base_url=os.environ["GRASP_BASE_URL"],
    )

    container = None
    try:
        print("\n1. Creating container...")
        container = await grasp.create()
        print(f"   ✓ Container created: {container.id}")
        print(f"   Status: {container.status}")
        print(f"   WebSocket: {container.browser.ws_endpoint}")

        print("\n2. Performing assertions...")
        assert container.id is not None
        assert container.status == "started"
        print("   ✓ All assertions passed")

    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        traceback.print_exc()

    finally:
        print("\n3. Cleaning up...")
        if container:
            try:
                await container.shutdown()
                print(f"   ✓ Container {container.id} shut down successfully")
            except Exception as e:
                print(f"   ❌ Failed to shutdown container: {e}")

        # Close the client
        try:
            await grasp.close()
            print("   ✓ Client closed")
        except Exception as e:
            print(f"   ❌ Failed to close client: {e}")

    print("\n" + "=" * 50)
    print("Test completed")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_single_container())