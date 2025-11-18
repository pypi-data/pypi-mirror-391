"""Workspace-related type definitions (organizations and projects)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class OrganizationSummary(BaseModel):
    """Represents an organization the user has access to."""

    id: int
    name: str
    is_personal: bool | None = None
    domain: str | None = None
    is_admin: bool | None = None


class ProjectSummary(BaseModel):
    """Represents a project available to the current user."""

    id: int
    organization_id: int
    name: str
    organization_name: str | None = None
    is_default: bool = Field(default=False)
    created_at: str | None = None
