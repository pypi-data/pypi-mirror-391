"""Guard configuration type definitions and helpers."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PolicyConfig(BaseModel):
    """Represents a policy entry inside a guard configuration."""

    policy_id: int
    policy_name: str
    policy_definition: str | None = None
    active: bool = True
    sensitivity: float = Field(0.0, ge=0.0, le=1.0)


class GuardPolicyGroup(BaseModel):
    """Policies that belong to a single guard."""

    guard_name: str
    policies: list[PolicyConfig] = Field(default_factory=list)


class GuardConfigurationConfig(BaseModel):
    """Top-level configuration wrapper sent to the Guardrails service."""

    guards: list[GuardPolicyGroup] = Field(default_factory=list)


class GuardConfigurationRecord(BaseModel):
    """Represents a stored guard configuration on the Guardrails service."""

    id: int
    name: str
    project_id: int | None = None
    config: GuardConfigurationConfig = Field(default_factory=GuardConfigurationConfig)
    created_at: str | None = None
    updated_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()

    def to_json(self, **kwargs: Any) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(**kwargs)


class GuardConfigurationBuilder:
    """Convenience helper for building GuardConfigurationConfig objects."""

    def __init__(self) -> None:
        self._guard_map: dict[str, GuardPolicyGroup] = {}

    def add_policy(
        self,
        guard_name: str,
        *,
        policy_id: int,
        policy_name: str,
        policy_definition: str | None = None,
        sensitivity: float = 0.0,
        active: bool = True,
    ) -> GuardConfigurationBuilder:
        """Add a policy for a guard, creating the guard group if needed."""

        guard_key = guard_name.strip()
        if not guard_key:
            raise ValueError("guard_name cannot be empty")

        group = self._guard_map.get(guard_key)
        if group is None:
            group = GuardPolicyGroup(guard_name=guard_key, policies=[])
            self._guard_map[guard_key] = group

        group.policies.append(
            PolicyConfig(
                policy_id=policy_id,
                policy_name=policy_name,
                policy_definition=policy_definition,
                sensitivity=sensitivity,
                active=active,
            )
        )
        return self

    def disable_guard(self, guard_name: str) -> GuardConfigurationBuilder:
        """Convenience helper to mark all policies for a guard as inactive."""

        guard_key = guard_name.strip()
        if not guard_key:
            raise ValueError("guard_name cannot be empty")

        group = self._guard_map.get(guard_key)
        if not group:
            return self
        for policy in group.policies:
            policy.active = False
        return self

    def build(self) -> GuardConfigurationConfig:
        """Return a GuardConfigurationConfig with the accumulated groups."""

        return GuardConfigurationConfig(guards=list(self._guard_map.values()))
