"""Custom exceptions for the General Analysis SDK."""

from typing import Any, Dict, Optional


class GeneralAnalysisError(Exception):
    """Base exception for all General Analysis SDK errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class AuthenticationError(GeneralAnalysisError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed. Check your API key."):
        super().__init__(message, status_code=401)


class GuardNotFoundError(GeneralAnalysisError):
    """Raised when a guard is not found."""

    def __init__(self, selector: str):
        message = f"Guard '{selector}' not found or access denied"
        super().__init__(message, status_code=404)


class ProjectScopeError(GeneralAnalysisError):
    """Raised when project scoping fails or is missing."""

    def __init__(
        self,
        message: str = "Project scope validation failed.",
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code=status_code, response_data=response_data)


class OrganizationContextError(GeneralAnalysisError):
    """Raised when organization metadata is missing for a request."""

    def __init__(
        self,
        message: str = "Organization context missing for project scope.",
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message,
            status_code=status_code or 500,
            response_data=response_data,
        )


class QuotaExceededError(GeneralAnalysisError):
    """Raised when guardrails quota limits are exceeded."""

    def __init__(
        self,
        message: str = "Guardrails quota exceeded.",
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message,
            status_code=status_code or 402,
            response_data=response_data,
        )


class GuardInvocationError(GeneralAnalysisError):
    """Raised when guard invocation fails on the server."""

    def __init__(
        self,
        message: str = "Guard invocation failed.",
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message,
            status_code=status_code or 502,
            response_data=response_data,
        )
