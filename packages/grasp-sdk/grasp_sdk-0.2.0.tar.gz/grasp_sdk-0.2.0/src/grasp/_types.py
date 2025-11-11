"""Type definitions for the Grasp SDK."""

from typing import Literal, Optional, TypedDict, Union

# Proxy types
ProxyType = Literal["mobile", "residential", "isp", "datacenter", "custom"]

# Container status
ContainerStatus = Literal["running", "stopped", "sleeping", "error"]


class ProxySettingsDict(TypedDict, total=False):
    """TypedDict for proxy settings."""

    enabled: bool
    type: ProxyType
    country: Optional[str]
    state: Optional[str]
    city: Optional[str]


class CreateOptionsDict(TypedDict, total=False):
    """TypedDict for container creation options."""

    idle_timeout: Optional[int]
    proxy: Optional[ProxySettingsDict]