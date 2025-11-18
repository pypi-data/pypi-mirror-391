"""Organizations resource for synchronous operations."""

from __future__ import annotations

from ..core.http_client import SyncHTTPClient
from ..types import OrganizationSummary


class Organizations:
    """Synchronous organizations resource."""

    def __init__(self, client: SyncHTTPClient):
        self._client = client

    def list(self) -> list[OrganizationSummary]:
        """List organizations available to the authenticated user."""

        response = self._client.get("/auth/me")
        organizations = response.get("organizations", []) if isinstance(response, dict) else []
        return [OrganizationSummary(**org) for org in organizations]
