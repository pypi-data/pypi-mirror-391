"""Helpers for resolving project scope."""

from __future__ import annotations

import os


def resolve_default_project_id(project_id: int | None = None) -> int | None:
    """
    Resolve the default project id for the SDK.

    Order of precedence:
        1. Explicit project_id argument.
        2. GA_PROJECT_ID environment variable (must be an int).
        3. None (API key scopes project automatically).
    """

    if project_id is not None:
        return project_id

    env_value = os.environ.get("GA_PROJECT_ID")
    if env_value is None:
        return None

    try:
        return int(env_value)
    except ValueError as exc:
        raise ValueError("GA_PROJECT_ID must be an integer") from exc


def merge_project_id(default_project_id: int | None, override: int | None) -> int | None:
    """Return the override if provided, otherwise the default."""

    if override is not None:
        return override
    return default_project_id
