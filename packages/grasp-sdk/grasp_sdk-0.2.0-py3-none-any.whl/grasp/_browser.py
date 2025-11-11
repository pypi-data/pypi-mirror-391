"""Browser session management."""

from typing import Dict, Any


class BrowserSession:
    """Browser session with CDP endpoint and live view URL."""

    def __init__(self, ws_endpoint: str, live_url: str):
        """Initialize browser session.

        Args:
            ws_endpoint: Chrome DevTools Protocol WebSocket endpoint
            live_url: Live view URL for observing the browser
        """
        self._ws_endpoint = ws_endpoint
        self._live_url = live_url

    @property
    def ws_endpoint(self) -> str:
        """Get Chrome DevTools Protocol WebSocket endpoint."""
        return self._ws_endpoint

    @property
    def live_url(self) -> str:
        """Get live view URL for observing the browser."""
        return self._live_url

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "ws_endpoint": self._ws_endpoint,
            "live_url": self._live_url,
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"BrowserSession(ws_endpoint={self._ws_endpoint!r}, live_url={self._live_url!r})"