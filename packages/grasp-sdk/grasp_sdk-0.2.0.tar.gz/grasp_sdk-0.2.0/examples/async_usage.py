#!/usr/bin/env python3
"""
Async usage example for Grasp Python SDK.

This example shows how to:
1. Use the async client
2. Create multiple containers concurrently
3. Use context managers for automatic cleanup
"""

import asyncio
import os
from grasp import AsyncGrasp


async def create_and_use_container(client: AsyncGrasp, idx: int):
    """Create and use a single container."""
    print(f"[Container {idx}] Creating...")

    container = await client.create(
        idle_timeout=60000,  # 60 seconds idle timeout
    )

    print(f"[Container {idx}] Created: {container.id}")
    print(f"[Container {idx}] WebSocket: {container.browser.ws_endpoint}")

    # Simulate some work
    await asyncio.sleep(2)

    # Shutdown
    print(f"[Container {idx}] Shutting down...")
    await container.shutdown()
    print(f"[Container {idx}] Shut down successfully")

    return container.id


async def main():
    # Use context manager for automatic cleanup
    async with AsyncGrasp(
        api_key=os.getenv("GRASP_API_KEY"),
        base_url=os.getenv("GRASP_BASE_URL", "https://api.getgrasp.ai"),
    ) as client:

        # Create multiple containers concurrently
        print("Creating 3 containers concurrently...")
        tasks = [
            create_and_use_container(client, i + 1)
            for i in range(3)
        ]

        # Wait for all containers to complete
        container_ids = await asyncio.gather(*tasks)

        print(f"\nAll containers completed: {container_ids}")

        # Example: Connect to existing container
        if container_ids:
            print(f"\nReconnecting to container {container_ids[0]}...")
            try:
                reconnected = await client.connect(container_ids[0])
                print(f"Reconnected to: {reconnected.id}")
                await reconnected.shutdown()
            except Exception as e:
                print(f"Could not reconnect (container may already be shut down): {e}")


if __name__ == "__main__":
    asyncio.run(main())