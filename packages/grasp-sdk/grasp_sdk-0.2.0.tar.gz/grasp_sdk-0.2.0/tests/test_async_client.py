"""Tests for asynchronous Grasp client."""

import os
import asyncio
import pytest
from grasp import AsyncGrasp, AsyncGraspContainer

# Try to import playwright for integration tests
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


@pytest.mark.asyncio
class TestAsyncGraspClient:
    """Test asynchronous Grasp client."""

    def setup_method(self, method):
        """Setup before each test method."""
        self.grasp = AsyncGrasp(
            api_key=os.environ["GRASP_API_KEY"],
            base_url=os.environ["GRASP_BASE_URL"],
        )
        self.containers_to_cleanup = []

    async def _cleanup_containers(self):
        """Clean up all containers created during the test."""
        for container in self.containers_to_cleanup:
            try:
                await container.shutdown()
                print(f"✓ Cleaned up container: {container.id}")
            except Exception as e:
                print(f"✗ Failed to cleanup container {getattr(container, 'id', 'unknown')}: {e}")
        self.containers_to_cleanup.clear()

    async def test_initialization(self):
        """Test async client initialization."""
        # With explicit parameters
        client = AsyncGrasp(
            api_key="test-key",
            base_url="http://localhost:3000",
        )
        assert client is not None
        assert isinstance(client, AsyncGrasp)
        await client.close()

        # With environment variables
        client = AsyncGrasp()
        assert client is not None
        assert isinstance(client, AsyncGrasp)
        await client.close()

    async def test_create_container(self):
        """Test creating a new container."""
        container = None
        try:
            container = await self.grasp.create()
            self.containers_to_cleanup.append(container)

            assert container.id is not None
            assert isinstance(container.id, str)
            assert container.status == "started"
            assert container.created_at is not None
            assert container.browser.ws_endpoint is not None
            assert container.browser.ws_endpoint.startswith(("ws://", "wss://"))
            assert container.browser.live_url is not None
            assert container.browser.live_url.startswith(("http://", "https://"))
        finally:
            # Always clean up
            if container:
                await container.shutdown()
                if container in self.containers_to_cleanup:
                    self.containers_to_cleanup.remove(container)

    async def test_create_container_with_options(self):
        """Test creating container with idle timeout option."""
        container = None
        try:
            container = await self.grasp.create(idle_timeout=60000)
            self.containers_to_cleanup.append(container)

            assert container.id is not None
            assert container.status == "started"
        finally:
            # Always clean up
            if container:
                await container.shutdown()
                if container in self.containers_to_cleanup:
                    self.containers_to_cleanup.remove(container)

    async def test_connect_to_container(self):
        """Test connecting to existing container by ID."""
        new_container = None
        try:
            # Create a new container
            new_container = await self.grasp.create()
            self.containers_to_cleanup.append(new_container)
            container_id = new_container.id

            # Connect to the existing container
            connected_container = await self.grasp.connect(container_id)
            # Note: connected_container is the same container, no need to shutdown twice

            assert connected_container.id == container_id
            assert connected_container.browser.ws_endpoint is not None
            assert connected_container.browser.live_url is not None
        finally:
            # Always clean up
            if new_container:
                await new_container.shutdown()
                if new_container in self.containers_to_cleanup:
                    self.containers_to_cleanup.remove(new_container)

    async def test_shutdown_container(self):
        """Test shutting down a container."""
        temp_container = await self.grasp.create()
        # Should not raise any exception
        await temp_container.shutdown()
        # Container is already shut down, no need to clean up again

    async def test_context_manager(self):
        """Test using async client as context manager."""
        container = None
        async with AsyncGrasp(
            api_key=os.environ["GRASP_API_KEY"],
            base_url=os.environ["GRASP_BASE_URL"],
        ) as client:
            container = await client.create()
            self.containers_to_cleanup.append(container)
            assert container.id is not None
            await container.shutdown()
            if container in self.containers_to_cleanup:
                self.containers_to_cleanup.remove(container)
        # Client should be closed automatically

    async def test_browser_endpoints(self):
        """Test that browser endpoints are valid."""
        container = None
        try:
            container = await self.grasp.create()
            self.containers_to_cleanup.append(container)

            assert container.browser.ws_endpoint is not None
            assert container.browser.ws_endpoint.startswith(("ws://", "wss://"))
            assert container.browser.live_url is not None
            assert container.browser.live_url.startswith(("http://", "https://"))
            assert container.id in container.browser.live_url
        finally:
            if container:
                await container.shutdown()
                if container in self.containers_to_cleanup:
                    self.containers_to_cleanup.remove(container)

    async def test_container_serialization(self):
        """Test container serialization without API key."""
        container = None
        try:
            container = await self.grasp.create()
            self.containers_to_cleanup.append(container)

            serialized = container.to_dict()

            assert serialized is not None
            assert serialized["id"] == container.id
            assert serialized["status"] == container.status
            assert serialized["created_at"] == container.created_at
            assert serialized["base_url"] == container._base_url
            assert serialized["browser"] is not None
            assert serialized["browser"]["ws_endpoint"] == container.browser.ws_endpoint
            assert serialized["browser"]["live_url"] == container.browser.live_url
            # API key should not be in serialized data
            assert "api_key" not in serialized
        finally:
            if container:
                await container.shutdown()
                if container in self.containers_to_cleanup:
                    self.containers_to_cleanup.remove(container)

    async def test_error_no_api_key(self):
        """Test error when no API key is provided."""
        # Temporarily remove API key
        original_key = os.environ.pop("GRASP_API_KEY", None)

        try:
            from grasp._exceptions import AuthenticationError
            with pytest.raises(AuthenticationError, match="Missing API key"):
                AsyncGrasp()
        finally:
            # Restore API key
            if original_key:
                os.environ["GRASP_API_KEY"] = original_key

    async def test_error_invalid_container_id(self):
        """Test error when connecting to invalid container ID."""
        with pytest.raises(Exception):  # Will be some API error
            await self.grasp.connect("invalid-container-id")

    async def test_error_shutdown_invalid_container(self):
        """Test error when shutting down container with invalid ID."""
        temp_container = None
        original_id = None
        try:
            temp_container = await self.grasp.create()
            self.containers_to_cleanup.append(temp_container)
            original_id = temp_container._id

            # Modify the ID to make it invalid
            temp_container._id = "invalid-id"

            with pytest.raises(Exception):  # Will be some API error
                await temp_container.shutdown()
        finally:
            # Restore original ID and clean up
            if temp_container and original_id:
                temp_container._id = original_id
                try:
                    await temp_container.shutdown()
                except Exception:
                    pass  # Ignore if already shut down
                if temp_container in self.containers_to_cleanup:
                    self.containers_to_cleanup.remove(temp_container)

    @pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="Playwright not installed")
    async def test_connect_browser_with_playwright(self):
        """Test connecting to browser via Playwright."""
        container = None
        try:
            container = await self.grasp.create()
            self.containers_to_cleanup.append(container)

            async with async_playwright() as p:
                # Connect to browser using CDP endpoint
                browser = await p.chromium.connect_over_cdp(
                    endpoint_url=container.browser.ws_endpoint
                )

                assert browser is not None
                assert browser.is_connected()

                await browser.close()
        finally:
            if container:
                await container.shutdown()
                if container in self.containers_to_cleanup:
                    self.containers_to_cleanup.remove(container)

    @pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="Playwright not installed")
    async def test_navigate_and_scrape_content(self):
        """Test navigating to a page and scraping content."""
        container = None
        try:
            container = await self.grasp.create()
            self.containers_to_cleanup.append(container)

            async with async_playwright() as p:
                # Connect to browser
                browser = await p.chromium.connect_over_cdp(
                    endpoint_url=container.browser.ws_endpoint
                )

                # Create context and page
                context = await browser.new_context()
                page = await context.new_page()

                # Navigate to page
                await page.goto("https://getgrasp.ai")

                # Get page info
                title = await page.title()
                url = page.url

                assert title is not None
                assert isinstance(title, str)
                assert url == "https://getgrasp.ai/"

                # Clean up
                await context.close()
                await browser.close()
        finally:
            if container:
                await container.shutdown()
                if container in self.containers_to_cleanup:
                    self.containers_to_cleanup.remove(container)

    # IMPORTANT: Remove or modify the concurrent test to avoid creating multiple containers
    # This test was creating 3 containers at once which can exhaust the E2B sandbox limit
    async def test_sequential_containers(self):
        """Test creating containers sequentially (not concurrently to avoid exhausting limits)."""
        containers = []
        try:
            # Create containers one by one
            for i in range(2):  # Only 2 containers instead of 3
                container = await self.grasp.create()
                containers.append(container)
                self.containers_to_cleanup.append(container)
                assert container.id is not None
                assert container.status == "started"
        finally:
            # Clean up all containers
            for container in containers:
                try:
                    await container.shutdown()
                except Exception as e:
                    print(f"Failed to cleanup container: {e}")
                if container in self.containers_to_cleanup:
                    self.containers_to_cleanup.remove(container)