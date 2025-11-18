"""Guards resource for asynchronous operations."""

from __future__ import annotations

import builtins
from typing import Any

from ..core.http_client import AsyncHTTPClient
from ..core.project import merge_project_id
from ..exceptions import GeneralAnalysisError, GuardNotFoundError
from ..types import (
    Guard,
    GuardConfigurationBuilder,
    GuardConfigurationConfig,
    GuardInvokeResult,
    GuardPolicyDetail,
    PaginatedLogsResponse,
)


class AsyncGuards:
    """Asynchronous guards resource."""

    def __init__(self, client: AsyncHTTPClient, default_project_id: int | None = None):
        self._client = client
        self._default_project_id = default_project_id
        self._guard_id_cache: dict[int, str] = {}

    def _resolve_project_id(self, project_id: int | None) -> int | None:
        return merge_project_id(self._default_project_id, project_id)

    async def list(self, project_id: int | None = None) -> builtins.list[Guard]:
        """List all available guards."""
        params = {}
        resolved_project_id = self._resolve_project_id(project_id)
        if resolved_project_id is not None:
            params["project_id"] = resolved_project_id

        response = await self._client.get("/guards", params=params or None)
        guards_data = response if isinstance(response, list) else [response]
        return [Guard(**guard) for guard in guards_data]

    async def list_policies(
        self, project_id: int | None = None
    ) -> builtins.list[GuardPolicyDetail]:
        """List guard policies accessible to the scoped project."""

        params = {}
        resolved_project_id = self._resolve_project_id(project_id)
        if resolved_project_id is not None:
            params["project_id"] = resolved_project_id

        response = await self._client.get("/policies", params=params or None)
        policies_data = response if isinstance(response, list) else [response]
        return [GuardPolicyDetail(**policy) for policy in policies_data]

    async def invoke(
        self,
        *,
        text: str,
        guard_id: int | str | None = None,
        guard_name: str | None = None,
        configuration_id: int | None = None,
        configuration: GuardConfigurationConfig | GuardConfigurationBuilder | None = None,
        project_id: int | None = None,
    ) -> GuardInvokeResult:
        """Invoke a guard or guard configuration asynchronously."""

        selectors = [
            guard_id is not None,
            bool(guard_name),
            configuration_id is not None,
            configuration is not None,
        ]
        if sum(selectors) != 1:
            raise ValueError(
                "Provide exactly one of guard_id, guard_name, configuration_id, or configuration"
            )

        resolved_guard_name = guard_name
        normalized_guard_id: int | None = None
        resolved_project_id = self._resolve_project_id(project_id)
        if guard_id is not None:
            normalized_guard_id = self._normalize_guard_id(guard_id)
            resolved_guard_name = await self._resolve_guard_name_by_id(
                normalized_guard_id,
                resolved_project_id,
            )

        payload = self._build_invoke_payload(
            text=text,
            guard_name=resolved_guard_name,
            configuration_id=configuration_id,
            configuration=configuration,
            project_id=resolved_project_id,
        )
        try:
            response = await self._client.post("/guards/invoke", data=payload)
            return GuardInvokeResult(**response)
        except GeneralAnalysisError as exc:
            if exc.status_code == 404:
                identifier = guard_name if normalized_guard_id is None else str(normalized_guard_id)
                if identifier:
                    raise GuardNotFoundError(identifier) from exc
            raise

    def _build_invoke_payload(
        self,
        *,
        text: str,
        guard_name: str | None,
        configuration_id: int | None,
        configuration: GuardConfigurationConfig | GuardConfigurationBuilder | None,
        project_id: int | None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"text": text}
        resolved_project_id = self._resolve_project_id(project_id)
        if resolved_project_id is not None:
            payload["project_id"] = resolved_project_id

        if guard_name:
            payload["guard_name"] = guard_name
        elif configuration_id is not None:
            payload["configuration_id"] = configuration_id
        else:
            payload["configuration"] = self._serialize_configuration(configuration)

        return payload

    def _serialize_configuration(
        self,
        configuration: GuardConfigurationConfig | GuardConfigurationBuilder | None,
    ) -> dict[str, Any]:
        if configuration is None:
            raise ValueError("configuration cannot be None")
        cfg: GuardConfigurationConfig
        if isinstance(configuration, GuardConfigurationBuilder):
            cfg = configuration.build()
        else:
            cfg = configuration
        return cfg.model_dump()

    async def list_logs(
        self,
        *,
        guard_name: str | None = None,
        project_id: int | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> PaginatedLogsResponse:
        """List guard invocation logs."""

        params: dict[str, Any] = {"page": page, "page_size": page_size}
        resolved_project_id = self._resolve_project_id(project_id)
        if resolved_project_id is not None:
            params["project_id"] = resolved_project_id
        if guard_name is not None:
            params["guard_name"] = guard_name

        response = await self._client.get("/guards/logs", params=params)
        return PaginatedLogsResponse(**response)

    async def _resolve_guard_name_by_id(self, guard_id: int, project_id: int | None) -> str:
        cached = self._guard_id_cache.get(guard_id)
        if cached:
            return cached

        try:
            params: dict[str, Any] = {}
            if project_id is not None:
                params["project_id"] = project_id
            response = await self._client.get("/guards", params=params or None)
        except GeneralAnalysisError as exc:
            if exc.status_code == 404:
                raise GuardNotFoundError(str(guard_id)) from exc
            raise

        guards_data = response if isinstance(response, list) else [response]

        for entry in guards_data:
            if not isinstance(entry, dict):
                continue
            if entry.get("id") == guard_id:
                guard = Guard(**entry)
                self._guard_id_cache[guard_id] = guard.name
                return guard.name

        raise GuardNotFoundError(str(guard_id))

    def _normalize_guard_id(self, guard_id: int | str) -> int:
        try:
            return int(guard_id)
        except (TypeError, ValueError) as exc:
            raise ValueError("guard_id must be an integer") from exc
