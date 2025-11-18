"""Synchronous client for the General Analysis SDK."""

from __future__ import annotations

import warnings
from typing import Any

from .core.auth import get_api_key, get_base_url
from .core.http_client import SyncHTTPClient
from .resources.guard_configurations import GuardConfigurations
from .resources.guards import Guards
from .resources.organizations import Organizations
from .resources.projects import Projects


class Client:
    """Synchronous client for interacting with the General Analysis API.

    Example:
        >>> import generalanalysis
        >>> client = generalanalysis.Client()
        >>> guards = client.guards.list()
        >>> result = client.guards.invoke(text="Check this text", guard_name="@pii_guard_llm")
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: int = 30,
    ):
        """Initialize the General Analysis client."""
        self.api_key = get_api_key(api_key)
        self.base_url = get_base_url(base_url)

        if not self.api_key:
            warnings.warn(
                "No API key found. Please set GA_API_KEY environment variable "
                "or pass api_key parameter. Some operations may fail.",
                UserWarning,
                stacklevel=2,
            )

        self._http_client = SyncHTTPClient(
            base_url=self.base_url, api_key=self.api_key, timeout=timeout
        )

        # Initialize resources
        self.guards = Guards(self._http_client)
        self.guard_configurations = GuardConfigurations(self._http_client)
        self.projects = Projects(self._http_client)
        self.organizations = Organizations(self._http_client)

    def close(self) -> None:
        """Close the client and cleanup resources."""
        self._http_client.close()

    def __enter__(self) -> Client:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    def __repr__(self) -> str:
        """String representation of the client."""
        return f"<GeneralAnalysis Client base_url='{self.base_url}'>"
