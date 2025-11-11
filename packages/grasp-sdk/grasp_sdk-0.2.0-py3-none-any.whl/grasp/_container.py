"""Container management classes."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional, TYPE_CHECKING
from urllib.parse import urlparse

from ._browser import BrowserSession

if TYPE_CHECKING:
    from ._http import HTTPClient, AsyncHTTPClient


def _generate_ws_endpoint(base_url: str, container_id: str) -> str:
    """Generate WebSocket endpoint URL if not provided by server."""
    parsed = urlparse(base_url)
    ws_scheme = "wss" if parsed.scheme == "https" else "ws"
    netloc = parsed.netloc
    return f"{ws_scheme}://{netloc}/v1/containers/{container_id}/cdp"


def _generate_live_url(base_url: str, container_id: str) -> str:
    """Generate live view URL if not provided by server."""
    parsed = urlparse(base_url)
    return f"{parsed.scheme}://{parsed.netloc}/v1/live/{container_id}"


class GraspContainer:
    """Represents a Grasp container instance."""

    def __init__(
        self,
        container_id: str,
        status: str,
        created_at: str,
        browser: BrowserSession,
        http_client: "HTTPClient",
        base_url: str,
    ):
        """Initialize container.

        Args:
            container_id: Unique container identifier
            status: Container status
            created_at: ISO timestamp of creation
            browser: Browser session information
            http_client: HTTP client for API calls
            base_url: Base URL of the API server
        """
        self._id = container_id
        self._status = status
        self._created_at = created_at
        self._browser = browser
        self._http_client = http_client
        self._base_url = base_url

    @classmethod
    def from_response(
        cls,
        response: Dict[str, Any],
        http_client: "HTTPClient",
        base_url: str,
    ) -> "GraspContainer":
        """Create container from API response."""
        container_id = response["id"]
        status = response.get("status", "running")
        created_at = response.get("createdAt", datetime.now(timezone.utc).isoformat())

        # Parse browser information
        browser_info = response.get("browser", {})
        ws_endpoint = browser_info.get("wsEndpoint") or _generate_ws_endpoint(
            base_url, container_id
        )
        live_url = browser_info.get("liveURL") or _generate_live_url(base_url, container_id)

        browser = BrowserSession(ws_endpoint=ws_endpoint, live_url=live_url)

        return cls(
            container_id=container_id,
            status=status,
            created_at=created_at,
            browser=browser,
            http_client=http_client,
            base_url=base_url,
        )

    @property
    def id(self) -> str:
        """Get container ID."""
        return self._id

    @property
    def status(self) -> str:
        """Get container status."""
        return self._status

    @property
    def created_at(self) -> str:
        """Get creation timestamp."""
        return self._created_at

    @property
    def browser(self) -> BrowserSession:
        """Get browser session."""
        return self._browser

    def shutdown(self) -> None:
        """Shut down the container."""
        self._http_client.post(f"/v1/containers/{self._id}/shutdown")
        self._status = "stopped"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation (excludes sensitive data)."""
        return {
            "id": self._id,
            "status": self._status,
            "created_at": self._created_at,
            "browser": self._browser.to_dict(),
            "base_url": self._base_url,
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"GraspContainer(id={self._id!r}, status={self._status!r})"


class AsyncGraspContainer:
    """Asynchronous version of GraspContainer."""

    def __init__(
        self,
        container_id: str,
        status: str,
        created_at: str,
        browser: BrowserSession,
        http_client: "AsyncHTTPClient",
        base_url: str,
    ):
        """Initialize async container.

        Args:
            container_id: Unique container identifier
            status: Container status
            created_at: ISO timestamp of creation
            browser: Browser session information
            http_client: Async HTTP client for API calls
            base_url: Base URL of the API server
        """
        self._id = container_id
        self._status = status
        self._created_at = created_at
        self._browser = browser
        self._http_client = http_client
        self._base_url = base_url

    @classmethod
    def from_response(
        cls,
        response: Dict[str, Any],
        http_client: "AsyncHTTPClient",
        base_url: str,
    ) -> "AsyncGraspContainer":
        """Create container from API response."""
        container_id = response["id"]
        status = response.get("status", "running")
        created_at = response.get("createdAt", datetime.now(timezone.utc).isoformat())

        # Parse browser information
        browser_info = response.get("browser", {})
        ws_endpoint = browser_info.get("wsEndpoint") or _generate_ws_endpoint(
            base_url, container_id
        )
        live_url = browser_info.get("liveURL") or _generate_live_url(base_url, container_id)

        browser = BrowserSession(ws_endpoint=ws_endpoint, live_url=live_url)

        return cls(
            container_id=container_id,
            status=status,
            created_at=created_at,
            browser=browser,
            http_client=http_client,
            base_url=base_url,
        )

    @property
    def id(self) -> str:
        """Get container ID."""
        return self._id

    @property
    def status(self) -> str:
        """Get container status."""
        return self._status

    @property
    def created_at(self) -> str:
        """Get creation timestamp."""
        return self._created_at

    @property
    def browser(self) -> BrowserSession:
        """Get browser session."""
        return self._browser

    async def shutdown(self) -> None:
        """Shut down the container."""
        await self._http_client.post(f"/v1/containers/{self._id}/shutdown")
        self._status = "stopped"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation (excludes sensitive data)."""
        return {
            "id": self._id,
            "status": self._status,
            "created_at": self._created_at,
            "browser": self._browser.to_dict(),
            "base_url": self._base_url,
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"AsyncGraspContainer(id={self._id!r}, status={self._status!r})"