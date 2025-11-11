"""
Grasp Python SDK

Python SDK for Grasp browser automation platform.

Basic usage:
    >>> from grasp import Grasp
    >>> client = Grasp(api_key="your-api-key")
    >>> container = client.create(idle_timeout=30000)
    >>> print(container.browser.ws_endpoint)
    >>> container.shutdown()

Async usage:
    >>> import asyncio
    >>> from grasp import AsyncGrasp
    >>> async def main():
    ...     async with AsyncGrasp(api_key="your-api-key") as client:
    ...         container = await client.create()
    ...         print(container.browser.ws_endpoint)
    ...         await container.shutdown()
    >>> asyncio.run(main())
"""

from ._async_client import AsyncGrasp
from ._browser import BrowserSession
from ._client import Grasp
from ._container import AsyncGraspContainer, GraspContainer
from ._exceptions import (
    APIConnectionError,
    APIError,
    APIResponseValidationError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    GraspError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServiceUnavailableError,
    UnprocessableEntityError,
)
from ._models import CreateOptions, ProxySettings
from ._types import ContainerStatus, ProxyType
from ._version import __version__

__all__ = [
    # Main clients
    "Grasp",
    "AsyncGrasp",
    # Container classes
    "GraspContainer",
    "AsyncGraspContainer",
    # Browser
    "BrowserSession",
    # Options and settings
    "CreateOptions",
    "ProxySettings",
    # Types
    "ProxyType",
    "ContainerStatus",
    # Exceptions
    "GraspError",
    "APIError",
    "APIConnectionError",
    "APITimeoutError",
    "APIResponseValidationError",
    "APIStatusError",
    "AuthenticationError",
    "BadRequestError",
    "NotFoundError",
    "PermissionDeniedError",
    "UnprocessableEntityError",
    "RateLimitError",
    "InternalServerError",
    "ServiceUnavailableError",
    # Version
    "__version__",
]
