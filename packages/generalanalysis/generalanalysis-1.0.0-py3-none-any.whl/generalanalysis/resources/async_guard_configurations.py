"""Guard configuration resource for asynchronous operations."""

from __future__ import annotations

from ..core.http_client import AsyncHTTPClient
from ..types import GuardConfigurationRecord


class AsyncGuardConfigurations:
    """Asynchronous guard configuration resource."""

    def __init__(self, client: AsyncHTTPClient):
        self._client = client

    async def list(self) -> list[GuardConfigurationRecord]:
        """List guard configurations visible to the API key's project."""

        response = await self._client.get("/guard-configs", params=None)
        if isinstance(response, list):
            records = response
        else:
            records = [response]
        return [GuardConfigurationRecord(**entry) for entry in records]
