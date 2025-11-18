"""Organizations resource for asynchronous operations."""

from __future__ import annotations

from ..core.http_client import AsyncHTTPClient
from ..types import OrganizationSummary


class AsyncOrganizations:
    """Asynchronous organizations resource."""

    def __init__(self, client: AsyncHTTPClient):
        self._client = client

    async def list(self) -> list[OrganizationSummary]:
        """List organizations available to the authenticated user."""

        response = await self._client.get("/auth/me")
        organizations = response.get("organizations", []) if isinstance(response, dict) else []
        return [OrganizationSummary(**org) for org in organizations]
