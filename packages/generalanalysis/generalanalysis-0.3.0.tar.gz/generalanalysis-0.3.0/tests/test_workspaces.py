"""Tests for workspace-related resources (projects and organizations)."""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from generalanalysis.resources.async_organizations import AsyncOrganizations
from generalanalysis.resources.async_projects import AsyncProjects
from generalanalysis.resources.organizations import Organizations
from generalanalysis.resources.projects import Projects


class TestProjects:
    def test_list_projects_with_org_filter(self):
        mock_client = Mock()
        mock_client.get.return_value = {
            "projects": [
                {
                    "id": 1,
                    "organization_id": 9,
                    "organization_name": "Default Org",
                    "name": "Default",
                    "is_default": True,
                    "created_at": "2024-01-01T00:00:00Z",
                }
            ]
        }

        resource = Projects(mock_client)
        projects = resource.list(organization_id=9)

        assert projects[0].name == "Default"
        mock_client.get.assert_called_once_with("/projects", params={"org_id": 9})

    @pytest.mark.asyncio
    async def test_async_list_projects(self):
        mock_client = AsyncMock()
        mock_client.get.return_value = {
            "projects": [
                {
                    "id": 2,
                    "organization_id": 11,
                    "organization_name": "Org B",
                    "name": "Sandbox",
                    "is_default": False,
                    "created_at": None,
                }
            ]
        }

        resource = AsyncProjects(mock_client)
        projects = await resource.list()

        assert projects[0].organization_id == 11
        mock_client.get.assert_awaited_once_with("/projects", params=None)


class TestOrganizations:
    def test_list_organizations(self):
        mock_client = Mock()
        mock_client.get.return_value = {
            "organizations": [
                {"id": 5, "name": "Acme Co", "is_admin": True, "is_personal": False},
            ],
        }

        resource = Organizations(mock_client)
        organizations = resource.list()

        assert organizations[0].name == "Acme Co"
        mock_client.get.assert_called_once_with("/auth/me")

    @pytest.mark.asyncio
    async def test_async_list_organizations(self):
        mock_client = AsyncMock()
        mock_client.get.return_value = {
            "organizations": [
                {"id": 6, "name": "Beta Org", "is_admin": False},
            ],
        }

        resource = AsyncOrganizations(mock_client)
        organizations = await resource.list()

        assert organizations[0].id == 6
        mock_client.get.assert_awaited_once_with("/auth/me")
