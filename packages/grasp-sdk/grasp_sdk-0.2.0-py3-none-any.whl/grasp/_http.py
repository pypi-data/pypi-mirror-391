"""HTTP client wrapper for the Grasp SDK."""

import json
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import httpx

from ._exceptions import (
    APIConnectionError,
    APIResponseValidationError,
    APIStatusError,
    APITimeoutError,
    make_status_error,
)


class HTTPClient:
    """Synchronous HTTP client wrapper."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = 60.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = httpx.Timeout(timeout, read=30.0, write=10.0, connect=5.0)
        self._client = httpx.Client(
            timeout=self.timeout,
            headers=self._get_default_headers(),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
        )

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for all requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "grasp-python/0.0.1",
        }

    def _make_url(self, path: str) -> str:
        """Construct full URL from path."""
        if not path.startswith("/"):
            path = f"/{path}"
        return urljoin(self.base_url, path)

    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle HTTP response and raise appropriate exceptions."""
        if response.status_code >= 400:
            try:
                error_body = response.text
            except Exception:
                error_body = None
            raise make_status_error(response, error_body)

        try:
            return response.json()
        except json.JSONDecodeError as e:
            raise APIResponseValidationError(
                f"Invalid JSON response: {e}", response, response.text
            )

    def post(
        self,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Make POST request."""
        url = self._make_url(path)

        try:
            response = self._client.post(url, json=json_data, **kwargs)
            return self._handle_response(response)
        except httpx.TimeoutException as e:
            raise APITimeoutError(f"Request timeout: {e}")
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Connection error: {e}")

    def get(self, path: str, **kwargs: Any) -> Any:
        """Make GET request."""
        url = self._make_url(path)

        try:
            response = self._client.get(url, **kwargs)
            return self._handle_response(response)
        except httpx.TimeoutException as e:
            raise APITimeoutError(f"Request timeout: {e}")
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Connection error: {e}")

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> "HTTPClient":
        """Enter context manager."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit context manager."""
        self.close()


class AsyncHTTPClient:
    """Asynchronous HTTP client wrapper."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = 60.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = httpx.Timeout(timeout, read=30.0, write=10.0, connect=5.0)
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            headers=self._get_default_headers(),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
        )

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for all requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "grasp-python/0.0.1",
        }

    def _make_url(self, path: str) -> str:
        """Construct full URL from path."""
        if not path.startswith("/"):
            path = f"/{path}"
        return urljoin(self.base_url, path)

    async def _handle_response(self, response: httpx.Response) -> Any:
        """Handle HTTP response and raise appropriate exceptions."""
        if response.status_code >= 400:
            try:
                error_body = response.text
            except Exception:
                error_body = None
            raise make_status_error(response, error_body)

        try:
            return response.json()
        except json.JSONDecodeError as e:
            raise APIResponseValidationError(
                f"Invalid JSON response: {e}", response, response.text
            )

    async def post(
        self,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Make POST request."""
        url = self._make_url(path)

        try:
            response = await self._client.post(url, json=json_data, **kwargs)
            return await self._handle_response(response)
        except httpx.TimeoutException as e:
            raise APITimeoutError(f"Request timeout: {e}")
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Connection error: {e}")

    async def get(self, path: str, **kwargs: Any) -> Any:
        """Make GET request."""
        url = self._make_url(path)

        try:
            response = await self._client.get(url, **kwargs)
            return await self._handle_response(response)
        except httpx.TimeoutException as e:
            raise APITimeoutError(f"Request timeout: {e}")
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Connection error: {e}")

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncHTTPClient":
        """Enter async context manager."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context manager."""
        await self.close()