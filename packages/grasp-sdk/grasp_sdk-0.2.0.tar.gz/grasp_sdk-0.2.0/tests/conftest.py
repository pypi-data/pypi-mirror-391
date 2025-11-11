"""Pytest configuration and fixtures for Grasp SDK tests."""

import os
import pytest
import asyncio
from typing import List, Optional

# Set test environment variables
os.environ["GRASP_API_KEY"] = "api-server-test"
os.environ["GRASP_BASE_URL"] = "http://localhost:3000"


class ContainerTracker:
    """Track all containers created during tests for cleanup."""

    def __init__(self):
        self.sync_containers: List = []
        self.async_containers: List = []

    def add_sync(self, container):
        """Add a sync container to track."""
        self.sync_containers.append(container)
        return container

    def add_async(self, container):
        """Add an async container to track."""
        self.async_containers.append(container)
        return container

    def cleanup_sync(self):
        """Clean up all sync containers."""
        for container in self.sync_containers:
            try:
                container.shutdown()
                print(f"✓ Cleaned up sync container: {container.id}")
            except Exception as e:
                print(f"✗ Failed to cleanup sync container {getattr(container, 'id', 'unknown')}: {e}")
        self.sync_containers.clear()

    async def cleanup_async(self):
        """Clean up all async containers."""
        for container in self.async_containers:
            try:
                await container.shutdown()
                print(f"✓ Cleaned up async container: {container.id}")
            except Exception as e:
                print(f"✗ Failed to cleanup async container {getattr(container, 'id', 'unknown')}: {e}")
        self.async_containers.clear()


@pytest.fixture
def container_tracker():
    """Provide a container tracker for test cleanup."""
    tracker = ContainerTracker()
    yield tracker
    # Clean up any remaining sync containers
    tracker.cleanup_sync()


@pytest.fixture
async def async_container_tracker():
    """Provide an async container tracker for test cleanup."""
    tracker = ContainerTracker()
    yield tracker
    # Clean up any remaining async containers
    await tracker.cleanup_async()


@pytest.fixture(autouse=True)
def cleanup_after_each_test(request):
    """Ensure cleanup after each test."""
    yield
    # This runs after each test
    # Force garbage collection to help with cleanup
    import gc
    gc.collect()


def pytest_configure(config):
    """Configure pytest to run tests sequentially."""
    # Disable parallel execution
    config.option.numprocesses = None
    config.option.dist = "no"