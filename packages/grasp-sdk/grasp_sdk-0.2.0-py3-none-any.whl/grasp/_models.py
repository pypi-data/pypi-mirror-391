"""Pydantic models for request and response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from ._types import ProxyType


class ProxySettings(BaseModel):
    """Proxy configuration settings."""

    enabled: bool = True
    type: ProxyType
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None


class CreateOptions(BaseModel):
    """Options for creating a new container."""

    model_config = ConfigDict(populate_by_name=True)

    idle_timeout: Optional[int] = Field(None, alias="idleTimeout", description="Idle timeout in milliseconds")
    proxy: Optional[ProxySettings] = None


class BrowserSessionResponse(BaseModel):
    """Browser session information from API response."""

    model_config = ConfigDict(populate_by_name=True)

    ws_endpoint: Optional[str] = Field(None, alias="wsEndpoint")
    live_url: Optional[str] = Field(None, alias="liveURL")


class ContainerResponse(BaseModel):
    """Container information from API response."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    status: str = "running"
    created_at: Optional[str] = Field(None, alias="createdAt")
    browser: Optional[BrowserSessionResponse] = None