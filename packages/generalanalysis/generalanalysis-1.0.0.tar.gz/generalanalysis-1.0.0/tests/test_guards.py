"""Tests for guards resource operations."""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from generalanalysis import GuardConfigurationBuilder, GuardConfigurationConfig, GuardNotFoundError
from generalanalysis.exceptions import GeneralAnalysisError
from generalanalysis.resources.async_guard_configurations import AsyncGuardConfigurations
from generalanalysis.resources.async_guards import AsyncGuards
from generalanalysis.resources.guard_configurations import GuardConfigurations
from generalanalysis.resources.guards import Guards


def _sample_guard_response():
    return [
        {
            "id": 1,
            "name": "@pii_guard",
            "description": None,
            "endpoint": "ga-pii-guard",
            "policies": [],
        },
        {
            "id": 2,
            "name": "@moderation_guard",
            "description": None,
            "endpoint": "ga-moderation",
            "policies": [],
        },
    ]


def _sample_invoke_response():
    return {
        "block": False,
        "latency_ms": 42.0,
        "policies": [
            {
                "name": "EMAIL_ADDRESS",
                "definition": "Detect emails",
                "pass": True,
                "violation_prob": 0.1,
            },
        ],
        "raw": {"bitstring": "0"},
    }


def _sample_policies_response():
    return [
        {
            "id": 1,
            "name": "EMAIL_ADDRESS",
            "definition": "Detect email addresses",
            "examples": ["test@example.com"],
            "guard_count": 2,
            "guards": ["@pii_guard", "@custom_guard"],
        }
    ]


def _sample_guard_detail(guard_id: int = 21, name: str = "@pii_guard") -> dict[str, object]:
    return {
        "id": guard_id,
        "name": name,
        "description": None,
        "endpoint": "ga-pii-guard",
        "system_prompt": None,
        "policies": [],
    }


class TestSyncGuards:
    def test_list_guards_calls_endpoint(self):
        mock_client = Mock()
        mock_client.get.return_value = _sample_guard_response()
        guards_resource = Guards(mock_client)

        guards = guards_resource.list()

        assert len(guards) == 2
        mock_client.get.assert_called_once_with("/guards", params=None)

    def test_invoke_with_guard_name(self):
        mock_client = Mock()
        mock_client.post.return_value = _sample_invoke_response()
        guards_resource = Guards(mock_client)

        result = guards_resource.invoke(text="hello world", guard_name="@pii_guard")

        assert result.block is False
        mock_client.post.assert_called_once_with(
            "/guards/invoke",
            data={
                "text": "hello world",
                "guard_name": "@pii_guard",
            },
        )

    def test_invoke_with_configuration_id(self):
        mock_client = Mock()
        mock_client.post.return_value = _sample_invoke_response()
        guards_resource = Guards(mock_client)

        guards_resource.invoke(text="hi", configuration_id=77)

        mock_client.post.assert_called_once_with(
            "/guards/invoke",
            data={
                "text": "hi",
                "configuration_id": 77,
            },
        )

    def test_invoke_with_guard_id(self):
        mock_client = Mock()
        mock_client.post.return_value = _sample_invoke_response()
        mock_client.get.return_value = [_sample_guard_detail(guard_id=21, name="@pii_guard")]
        guards_resource = Guards(mock_client)

        guards_resource.invoke(text="hello", guard_id=21)

        mock_client.get.assert_called_once_with("/guards", params=None)
        mock_client.post.assert_called_once_with(
            "/guards/invoke",
            data={
                "text": "hello",
                "guard_name": "@pii_guard",
            },
        )

    def test_invoke_with_guard_id_string(self):
        mock_client = Mock()
        mock_client.post.return_value = _sample_invoke_response()
        mock_client.get.return_value = [_sample_guard_detail(guard_id=21, name="@pii_guard")]
        guards_resource = Guards(mock_client)

        guards_resource.invoke(text="hello", guard_id="21")

        mock_client.get.assert_called_once_with("/guards", params=None)
        mock_client.post.assert_called_once_with(
            "/guards/invoke",
            data={"text": "hello", "guard_name": "@pii_guard"},
        )

    def test_invoke_with_guard_id_invalid_string(self):
        guards_resource = Guards(Mock())

        with pytest.raises(ValueError, match="guard_id must be an integer"):
            guards_resource.invoke(text="hello", guard_id="twenty-one")

    def test_invoke_with_inline_configuration_builder(self):
        mock_client = Mock()
        mock_client.post.return_value = _sample_invoke_response()
        builder = GuardConfigurationBuilder()
        builder.add_policy(
            guard_name="@pii_guard",
            policy_id=1,
            policy_name="EMAIL_ADDRESS",
            sensitivity=0.5,
        )
        guards_resource = Guards(mock_client)

        guards_resource.invoke(text="hi", configuration=builder)

        payload = mock_client.post.call_args.kwargs["data"]
        assert "configuration" in payload
        assert payload["configuration"]["guards"][0]["guard_name"] == "@pii_guard"

    def test_invoke_requires_single_selector(self):
        guards_resource = Guards(Mock())
        with pytest.raises(
            ValueError, match="guard_id, guard_name, configuration_id, or configuration"
        ):
            guards_resource.invoke(text="hi", guard_name="@a", configuration_id=1)

    def test_invoke_guard_not_found_maps_exception(self):
        mock_client = Mock()
        mock_client.post.side_effect = GeneralAnalysisError("missing", status_code=404)
        guards_resource = Guards(mock_client)

        with pytest.raises(GuardNotFoundError):
            guards_resource.invoke(text="hi", guard_name="@missing")

    def test_invoke_guard_id_not_found_maps_exception(self):
        mock_client = Mock()
        mock_client.get.return_value = []
        guards_resource = Guards(mock_client)

        with pytest.raises(GuardNotFoundError):
            guards_resource.invoke(text="hello", guard_id=404)

        mock_client.post.assert_not_called()

    def test_list_logs_includes_guard_name_filter(self):
        mock_client = Mock()
        mock_client.get.return_value = {
            "items": [
                {
                    "id": 1,
                    "project_id": 9,
                    "guard_id": 2,
                    "guard_name": "@pii_guard",
                    "input_text": "foo",
                    "created_at": "2024-01-01T00:00:00",
                    "result": _sample_invoke_response(),
                }
            ],
            "total": 1,
            "page": 1,
            "page_size": 50,
            "total_pages": 1,
        }
        guards_resource = Guards(mock_client)

        logs = guards_resource.list_logs(guard_name="@pii_guard", page=2, page_size=10)

        assert logs.items[0].guard_name == "@pii_guard"
        mock_client.get.assert_called_once_with(
            "/guards/logs",
            params={"page": 2, "page_size": 10, "guard_name": "@pii_guard"},
        )

    def test_list_policies(self):
        mock_client = Mock()
        mock_client.get.return_value = _sample_policies_response()
        guards_resource = Guards(mock_client)

        policies = guards_resource.list_policies()

        assert policies[0].name == "EMAIL_ADDRESS"
        mock_client.get.assert_called_once_with("/policies", params=None)


class TestAsyncGuards:
    @pytest.mark.asyncio
    async def test_async_list_guards(self):
        mock_client = AsyncMock()
        mock_client.get.return_value = _sample_guard_response()
        guards_resource = AsyncGuards(mock_client)

        guards = await guards_resource.list()

        assert guards[0].name == "@pii_guard"
        mock_client.get.assert_awaited_once_with("/guards", params=None)

    @pytest.mark.asyncio
    async def test_async_invoke_guard_name(self):
        mock_client = AsyncMock()
        mock_client.post.return_value = _sample_invoke_response()
        guards_resource = AsyncGuards(mock_client)

        await guards_resource.invoke(text="hello", guard_name="@pii_guard")

        mock_client.post.assert_awaited_once_with(
            "/guards/invoke",
            data={"text": "hello", "guard_name": "@pii_guard"},
        )

    @pytest.mark.asyncio
    async def test_async_invoke_guard_id(self):
        mock_client = AsyncMock()
        mock_client.post.return_value = _sample_invoke_response()
        mock_client.get.return_value = [_sample_guard_detail(guard_id=55)]
        guards_resource = AsyncGuards(mock_client)

        await guards_resource.invoke(text="hello", guard_id=55)

        mock_client.get.assert_awaited_once_with("/guards", params=None)
        mock_client.post.assert_awaited_once_with(
            "/guards/invoke",
            data={"text": "hello", "guard_name": "@pii_guard"},
        )

    @pytest.mark.asyncio
    async def test_async_invoke_with_guard_id_string(self):
        mock_client = AsyncMock()
        mock_client.post.return_value = _sample_invoke_response()
        mock_client.get.return_value = [_sample_guard_detail(guard_id=32, name="@async_guard")]
        guards_resource = AsyncGuards(mock_client)

        await guards_resource.invoke(text="hello", guard_id="32")

        mock_client.get.assert_awaited_once_with("/guards", params=None)
        mock_client.post.assert_awaited_once_with(
            "/guards/invoke",
            data={"text": "hello", "guard_name": "@async_guard"},
        )

    @pytest.mark.asyncio
    async def test_async_invoke_guard_id_invalid_string(self):
        guards_resource = AsyncGuards(AsyncMock())

        with pytest.raises(ValueError, match="guard_id must be an integer"):
            await guards_resource.invoke(text="hello", guard_id="abc")

    @pytest.mark.asyncio
    async def test_async_inline_configuration(self):
        mock_client = AsyncMock()
        mock_client.post.return_value = _sample_invoke_response()
        config = GuardConfigurationConfig(guards=[])
        guards_resource = AsyncGuards(mock_client)

        await guards_resource.invoke(text="hello", configuration=config)

        payload = mock_client.post.call_args.kwargs["data"]
        assert "configuration" in payload
        assert payload["configuration"]["guards"] == []

    @pytest.mark.asyncio
    async def test_async_list_policies(self):
        mock_client = AsyncMock()
        mock_client.get.return_value = _sample_policies_response()
        guards_resource = AsyncGuards(mock_client)

        policies = await guards_resource.list_policies()

        assert policies[0].guard_count == 2
        mock_client.get.assert_awaited_once_with("/policies", params=None)

    @pytest.mark.asyncio
    async def test_async_guard_id_not_found_maps_exception(self):
        mock_client = AsyncMock()
        mock_client.get.return_value = []
        guards_resource = AsyncGuards(mock_client)

        with pytest.raises(GuardNotFoundError):
            await guards_resource.invoke(text="oops", guard_id=999)

        mock_client.post.assert_not_awaited()


class TestGuardConfigurations:
    def test_list_guard_configurations(self):
        mock_client = Mock()
        mock_client.get.return_value = [
            {
                "id": 7,
                "name": "default",
                "project_id": 9,
                "config": {"guards": []},
            }
        ]
        configs_resource = GuardConfigurations(mock_client)

        configs = configs_resource.list()

        assert configs[0].id == 7
        mock_client.get.assert_called_once_with("/guard-configs", params=None)


class TestAsyncGuardConfigurations:
    @pytest.mark.asyncio
    async def test_async_list_guard_configurations(self):
        mock_client = AsyncMock()
        mock_client.get.return_value = [
            {
                "id": 8,
                "name": "override",
                "project_id": 10,
                "config": {"guards": []},
            }
        ]
        configs_resource = AsyncGuardConfigurations(mock_client)

        configs = await configs_resource.list()

        assert configs[0].name == "override"
        mock_client.get.assert_awaited_once_with("/guard-configs", params=None)
