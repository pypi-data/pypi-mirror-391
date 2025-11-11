"""Synchronous Grasp client implementation."""

import os
from typing import Any, Dict, Optional

from ._container import GraspContainer
from ._exceptions import AuthenticationError
from ._http import HTTPClient
from ._models import CreateOptions


DEFAULT_BASE_URL = "https://api.getgrasp.ai"


class Grasp:
    """Synchronous client for Grasp API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 60.0,
    ):
        """Initialize Grasp client.

        Args:
            api_key: API key for authentication. If not provided, will try to
                    read from GRASP_API_KEY environment variable.
            base_url: Base URL for the API. If not provided, will try to read
                     from GRASP_BASE_URL environment variable or use default.
            timeout: Request timeout in seconds
        """
        # Resolve API key
        self._api_key = api_key or os.environ.get("GRASP_API_KEY")
        if not self._api_key:
            raise AuthenticationError(
                "Missing API key. Provide one via Grasp(api_key='...') "
                "or set GRASP_API_KEY in your environment."
            )

        # Resolve base URL
        self._base_url = (
            base_url or os.environ.get("GRASP_BASE_URL", DEFAULT_BASE_URL)
        ).rstrip("/")

        # Initialize HTTP client
        self._http = HTTPClient(
            base_url=self._base_url,
            api_key=self._api_key,
            timeout=timeout,
        )

    def create(self, **options: Any) -> GraspContainer:
        """Create a new container.

        Args:
            **options: Container creation options
                - idle_timeout (int): Idle timeout in milliseconds
                - proxy (dict): Proxy configuration with fields:
                    - enabled (bool): Whether to enable proxy
                    - type (str): Proxy type (mobile, residential, isp, datacenter, custom)
                    - country (str): Country code
                    - state (str): State code
                    - city (str): City name

        Returns:
            GraspContainer: The created container

        Example:
            >>> client = Grasp()
            >>> container = client.create(
            ...     idle_timeout=30000,
            ...     proxy={
            ...         "enabled": True,
            ...         "type": "residential",
            ...         "country": "US"
            ...     }
            ... )
        """
        # Validate options with Pydantic if needed
        create_opts = CreateOptions(**options) if options else CreateOptions()

        # Make API request
        response = self._http.post(
            "/v1/containers",
            json_data=create_opts.model_dump(exclude_none=True, by_alias=True),
        )

        # Create container from response
        return GraspContainer.from_response(
            response=response,
            http_client=self._http,
            base_url=self._base_url,
        )

    def connect(self, container_id: str) -> GraspContainer:
        """Connect to an existing container.

        This will wake up the container if it's sleeping.

        Args:
            container_id: The ID of the container to connect to

        Returns:
            GraspContainer: The connected container

        Example:
            >>> client = Grasp()
            >>> container = client.connect("container-123")
        """
        # Make API request to connect
        response = self._http.post(f"/v1/containers/{container_id}/connect")

        # Create container from response
        return GraspContainer.from_response(
            response=response,
            http_client=self._http,
            base_url=self._base_url,
        )

    def close(self) -> None:
        """Close the HTTP client."""
        self._http.close()

    def __enter__(self) -> "Grasp":
        """Enter context manager."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit context manager."""
        self.close()

    def __repr__(self) -> str:
        """String representation."""
        return f"Grasp(base_url={self._base_url!r})"