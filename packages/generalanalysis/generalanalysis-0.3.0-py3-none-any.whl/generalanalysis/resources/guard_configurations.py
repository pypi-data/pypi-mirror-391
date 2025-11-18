"""Guard configuration resource for synchronous operations."""

from __future__ import annotations

from ..core.http_client import SyncHTTPClient
from ..core.project import merge_project_id
from ..types import GuardConfigurationRecord


class GuardConfigurations:
    """Synchronous guard configuration resource."""

    def __init__(self, client: SyncHTTPClient, default_project_id: int | None = None):
        self._client = client
        self._default_project_id = default_project_id

    def _resolve_project_id(self, project_id: int | None) -> int | None:
        return merge_project_id(self._default_project_id, project_id)

    def list(self, project_id: int | None = None) -> list[GuardConfigurationRecord]:
        """List guard configurations visible to the scoped project."""

        params = {}
        resolved_project_id = self._resolve_project_id(project_id)
        if resolved_project_id is not None:
            params["project_id"] = resolved_project_id

        response = self._client.get("/guard-configs", params=params or None)
        if isinstance(response, list):
            records = response
        else:
            records = [response]
        return [GuardConfigurationRecord(**entry) for entry in records]
