"""
General Analysis - Python SDK for AI Guardrails

A simple and intuitive SDK for invoking and managing AI guardrails,
modeled after the design patterns of OpenAI and Anthropic SDKs.

Basic usage:
    >>> import generalanalysis
    >>> client = generalanalysis.Client()
    >>> guards = client.guards.list()
    >>> result = client.guards.invoke(text="Check this text", guard_name="@pii_guard_llm")

Async usage:
    >>> import asyncio
    >>> import generalanalysis
    >>>
    >>> async def main():
    ...     client = generalanalysis.AsyncClient()
    ...     result = await client.guards.invoke(text="Check this text", guard_name="@pii_guard_llm")
    ...     await client.close()
    >>>
    >>> asyncio.run(main())
"""

from .__version__ import __version__
from .async_client import AsyncClient
from .client import Client
from .exceptions import (
    AuthenticationError,
    GeneralAnalysisError,
    GuardInvocationError,
    GuardNotFoundError,
    OrganizationContextError,
    ProjectScopeError,
    QuotaExceededError,
)
from .types import (
    Guard,
    GuardConfigurationBuilder,
    GuardConfigurationConfig,
    GuardConfigurationRecord,
    GuardInvokeResult,
    GuardLog,
    GuardPolicy,
    GuardPolicyDetail,
    GuardPolicyGroup,
    OrganizationSummary,
    PaginatedLogsResponse,
    PolicyConfig,
    PolicyEvaluation,
    ProjectSummary,
)

__all__ = [
    # Version
    "__version__",
    # Clients
    "Client",
    "AsyncClient",
    # Types
    "Guard",
    "GuardPolicy",
    "GuardPolicyDetail",
    "GuardConfigurationConfig",
    "GuardConfigurationBuilder",
    "GuardConfigurationRecord",
    "GuardPolicyGroup",
    "PolicyConfig",
    "GuardInvokeResult",
    "PolicyEvaluation",
    "GuardLog",
    "PaginatedLogsResponse",
    "OrganizationSummary",
    "ProjectSummary",
    # Exceptions
    "GeneralAnalysisError",
    "AuthenticationError",
    "GuardNotFoundError",
    "GuardInvocationError",
    "ProjectScopeError",
    "OrganizationContextError",
    "QuotaExceededError",
]
