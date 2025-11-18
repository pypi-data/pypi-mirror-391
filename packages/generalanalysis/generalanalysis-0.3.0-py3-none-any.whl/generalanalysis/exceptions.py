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
