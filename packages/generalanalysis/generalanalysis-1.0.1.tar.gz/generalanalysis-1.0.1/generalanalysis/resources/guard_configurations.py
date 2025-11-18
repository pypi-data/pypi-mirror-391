"""Guard configuration resource for synchronous operations."""

from __future__ import annotations

from ..core.http_client import SyncHTTPClient
from ..types import GuardConfigurationRecord


class GuardConfigurations:
    """Synchronous guard configuration resource."""

    def __init__(self, client: SyncHTTPClient):
        self._client = client

    def list(self) -> list[GuardConfigurationRecord]:
        """List guard configurations visible to the API key's project."""

        response = self._client.get("/guard-configs", params=None)
        if isinstance(response, list):
            records = response
        else:
            records = [response]
        return [GuardConfigurationRecord(**entry) for entry in records]
