"""Projects resource for asynchronous operations."""

from __future__ import annotations

import builtins
from typing import Any

from ..core.http_client import AsyncHTTPClient
from ..types import ProjectSummary


class AsyncProjects:
    """Asynchronous projects resource."""

    def __init__(self, client: AsyncHTTPClient):
        self._client = client

    async def list(self, organization_id: int | None = None) -> builtins.list[ProjectSummary]:
        """List projects the authenticated user can access."""

        params: dict[str, Any] = {}
        if organization_id is not None:
            params["org_id"] = organization_id

        response = await self._client.get("/projects", params=params or None)
        projects_data = self._extract_projects(response)
        return [ProjectSummary(**project) for project in projects_data]

    @staticmethod
    def _extract_projects(response: Any) -> builtins.list[dict[str, Any]]:
        if isinstance(response, dict):
            data = response.get("projects", [])
        else:
            data = response

        if data is None:
            return []
        if not isinstance(data, list):
            data = [data]
        return [project for project in data if isinstance(project, dict)]
