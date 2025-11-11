"""Tests for synchronous Grasp client."""

import os
import time
import pytest
from grasp import Grasp, GraspContainer

# Try to import playwright for integration tests
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class TestGraspClient:
    """Test synchronous Grasp client."""

    def setup_method(self, method):
        """Setup before each test method."""
        self.grasp = Grasp(
            api_key=os.environ["GRASP_API_KEY"],
            base_url=os.environ["GRASP_BASE_URL"],
        )
        self.containers_to_cleanup = []

    def teardown_method(self, method):
        """Cleanup after each test method."""
        # Clean up any containers that weren't cleaned up in the test
        for container in self.containers_to_cleanup:
            try:
                container.shutdown()
                print(f"✓ Cleaned up container in teardown: {container.id}")
            except Exception as e:
                print(f"✗ Failed to cleanup container {getattr(container, 'id', 'unknown')}: {e}")
        self.containers_to_cleanup.clear()

    def test_initialization(self):
        """Test client initialization."""
        # With explicit parameters
        client = Grasp(
            api_key="test-key",
            base_url="http://localhost:3000",
        )
        assert client is not None
        assert isinstance(client, Grasp)

        # With environment variables
        client = Grasp()
        assert client is not None
        assert isinstance(client, Grasp)

    def test_create_container(self):
        """Test creating a new container."""
        container = None
        try:
            container = self.grasp.create()
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
                container.shutdown()
                if container in self.containers_to_cleanup:
                    self.containers_to_cleanup.remove(container)

    def test_create_container_with_options(self):
        """Test creating container with idle timeout option."""
        container = None
        try:
            container = self.grasp.create(idle_timeout=60000)
            self.containers_to_cleanup.append(container)

            assert container.id is not None
            assert container.status == "started"
        finally:
            # Always clean up
            if container:
                container.shutdown()
                if container in self.containers_to_cleanup:
                    self.containers_to_cleanup.remove(container)

    def test_connect_to_container(self):
        """Test connecting to existing container by ID."""
        new_container = None
        try:
            # Create a new container
            new_container = self.grasp.create()
            self.containers_to_cleanup.append(new_container)
            container_id = new_container.id

            # Connect to the existing container
            connected_container = self.grasp.connect(container_id)
            # Note: connected_container is the same container, no need to shutdown twice

            assert connected_container.id == container_id
            assert connected_container.browser.ws_endpoint is not None
            assert connected_container.browser.live_url is not None
        finally:
            # Always clean up
            if new_container:
                new_container.shutdown()
                if new_container in self.containers_to_cleanup:
                    self.containers_to_cleanup.remove(new_container)

    def test_shutdown_container(self):
        """Test shutting down a container."""
        temp_container = self.grasp.create()
        # Should not raise any exception
        temp_container.shutdown()
        # Container is already shut down, no need to clean up again

    def test_browser_endpoints(self):
        """Test that browser endpoints are valid."""
        container = None
        try:
            container = self.grasp.create()
            self.containers_to_cleanup.append(container)

            assert container.browser.ws_endpoint is not None
            assert container.browser.ws_endpoint.startswith(("ws://", "wss://"))
            assert container.browser.live_url is not None
            assert container.browser.live_url.startswith(("http://", "https://"))
            assert container.id in container.browser.live_url
        finally:
            if container:
                container.shutdown()
                if container in self.containers_to_cleanup:
                    self.containers_to_cleanup.remove(container)

    def test_container_serialization(self):
        """Test container serialization without API key."""
        container = None
        try:
            container = self.grasp.create()
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
                container.shutdown()
                if container in self.containers_to_cleanup:
                    self.containers_to_cleanup.remove(container)

    def test_browser_session_serialization(self):
        """Test browser session serialization."""
        container = None
        try:
            container = self.grasp.create()
            self.containers_to_cleanup.append(container)

            browser_serialized = container.browser.to_dict()

            assert browser_serialized is not None
            assert browser_serialized["ws_endpoint"] == container.browser.ws_endpoint
            assert browser_serialized["live_url"] == container.browser.live_url
        finally:
            if container:
                container.shutdown()
                if container in self.containers_to_cleanup:
                    self.containers_to_cleanup.remove(container)

    def test_error_no_api_key(self):
        """Test error when no API key is provided."""
        # Temporarily remove API key
        original_key = os.environ.pop("GRASP_API_KEY", None)

        try:
            from grasp._exceptions import AuthenticationError
            with pytest.raises(AuthenticationError, match="Missing API key"):
                Grasp()
        finally:
            # Restore API key
            if original_key:
                os.environ["GRASP_API_KEY"] = original_key

    def test_error_invalid_container_id(self):
        """Test error when connecting to invalid container ID."""
        with pytest.raises(Exception):  # Will be some API error
            self.grasp.connect("invalid-container-id")

    def test_error_shutdown_invalid_container(self):
        """Test error when shutting down container with invalid ID."""
        temp_container = None
        original_id = None
        try:
            temp_container = self.grasp.create()
            self.containers_to_cleanup.append(temp_container)
            original_id = temp_container._id

            # Modify the ID to make it invalid
            temp_container._id = "invalid-id"

            with pytest.raises(Exception):  # Will be some API error
                temp_container.shutdown()
        finally:
            # Restore original ID and clean up
            if temp_container and original_id:
                temp_container._id = original_id
                try:
                    temp_container.shutdown()
                except Exception:
                    pass  # Ignore if already shut down
                if temp_container in self.containers_to_cleanup:
                    self.containers_to_cleanup.remove(temp_container)

    @pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="Playwright not installed")
    def test_connect_browser_with_playwright(self):
        """Test connecting to browser via Playwright."""
        container = None
        try:
            container = self.grasp.create()
            self.containers_to_cleanup.append(container)

            with sync_playwright() as p:
                # Connect to browser using CDP endpoint
                browser = p.chromium.connect_over_cdp(
                    endpoint_url=container.browser.ws_endpoint
                )

                assert browser is not None
                assert browser.is_connected()

                browser.close()
        finally:
            if container:
                container.shutdown()
                if container in self.containers_to_cleanup:
                    self.containers_to_cleanup.remove(container)

    @pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="Playwright not installed")
    def test_navigate_and_scrape_content(self):
        """Test navigating to a page and scraping content."""
        container = None
        try:
            container = self.grasp.create()
            self.containers_to_cleanup.append(container)

            with sync_playwright() as p:
                # Connect to browser
                browser = p.chromium.connect_over_cdp(
                    endpoint_url=container.browser.ws_endpoint
                )

                # Create context and page
                context = browser.new_context()
                page = context.new_page()

                # Navigate to page
                page.goto("https://getgrasp.ai")

                # Get page info
                title = page.title()
                url = page.url

                assert title is not None
                assert isinstance(title, str)
                assert url == "https://getgrasp.ai/"

                # Clean up
                context.close()
                browser.close()
        finally:
            if container:
                container.shutdown()
                if container in self.containers_to_cleanup:
                    self.containers_to_cleanup.remove(container)