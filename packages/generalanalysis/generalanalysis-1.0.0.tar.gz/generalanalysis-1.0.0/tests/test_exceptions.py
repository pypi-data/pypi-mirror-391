"""Tests for custom exceptions."""

import pytest

from generalanalysis import (
    AuthenticationError,
    GeneralAnalysisError,
    GuardInvocationError,
    GuardNotFoundError,
    OrganizationContextError,
    ProjectScopeError,
    QuotaExceededError,
)
from generalanalysis.core.http_client import SyncHTTPClient


class TestExceptions:
    """Tests for exception classes."""

    def test_general_analysis_error(self):
        """Test GeneralAnalysisError creation and attributes."""
        error = GeneralAnalysisError(
            "Test error",
            status_code=500,
            response_data={"detail": "Server error"},
        )
        assert str(error) == "Test error"
        assert error.status_code == 500
        assert error.response_data == {"detail": "Server error"}

    def test_general_analysis_error_minimal(self):
        """Test GeneralAnalysisError with minimal args."""
        error = GeneralAnalysisError("Simple error")
        assert str(error) == "Simple error"
        assert error.status_code is None
        assert error.response_data is None

    def test_authentication_error(self):
        """Test AuthenticationError creation."""
        error = AuthenticationError()
        assert "Authentication failed" in str(error)
        assert error.status_code == 401

    def test_authentication_error_custom_message(self):
        """Test AuthenticationError with custom message."""
        error = AuthenticationError("Invalid API key format")
        assert str(error) == "Invalid API key format"
        assert error.status_code == 401

    def test_guard_not_found_error(self):
        """Test GuardNotFoundError creation."""
        error = GuardNotFoundError(selector="@pii_guard")
        assert "@pii_guard" in str(error)
        assert "not found" in str(error)
        assert error.status_code == 404

    def test_project_scope_error(self):
        """Test ProjectScopeError creation."""
        error = ProjectScopeError("Project scope required", status_code=403)
        assert "Project scope required" in str(error)
        assert error.status_code == 403

    def test_organization_context_error_defaults(self):
        """Test OrganizationContextError default status."""
        error = OrganizationContextError()
        assert error.status_code == 500

    def test_quota_exceeded_error_defaults(self):
        """Test QuotaExceededError default status."""
        error = QuotaExceededError()
        assert error.status_code == 402

    def test_guard_invocation_error_defaults(self):
        """Test GuardInvocationError default status."""
        error = GuardInvocationError()
        assert error.status_code == 502

    def test_exception_inheritance(self):
        """Test that all exceptions inherit from GeneralAnalysisError."""
        assert issubclass(AuthenticationError, GeneralAnalysisError)
        assert issubclass(GuardNotFoundError, GeneralAnalysisError)
        assert issubclass(ProjectScopeError, GeneralAnalysisError)
        assert issubclass(OrganizationContextError, GeneralAnalysisError)
        assert issubclass(QuotaExceededError, GeneralAnalysisError)
        assert issubclass(GuardInvocationError, GeneralAnalysisError)

    def test_exception_catching(self):
        """Test that exceptions can be caught properly."""
        # Specific exception
        with pytest.raises(GuardNotFoundError):
            raise GuardNotFoundError(selector="@pii_guard")

        # Base exception catches derived
        with pytest.raises(GeneralAnalysisError):
            raise AuthenticationError()

        # Base exception catches all SDK errors
        with pytest.raises(GeneralAnalysisError):
            raise GuardNotFoundError(selector="@pii_guard")

        with pytest.raises(GeneralAnalysisError):
            raise ProjectScopeError("Project scope missing")


class TestHTTPClientErrorMapping:
    """Tests for mapping server errors to specialized exceptions."""

    def _assert_exception(
        self,
        status: int,
        payload: dict[str, object],
        exc_type: type[Exception],
    ):
        client = SyncHTTPClient(base_url="http://example.com")
        try:
            with pytest.raises(exc_type):
                client._handle_response_error(status, payload)
        finally:
            client.close()

    def test_maps_organization_context_error(self):
        """Server org context failures raise OrganizationContextError."""
        self._assert_exception(
            500,
            {"detail": "Organization context missing for project scope"},
            OrganizationContextError,
        )

    def test_maps_project_scope_error(self):
        """Project scope failures raise ProjectScopeError."""
        self._assert_exception(
            403,
            {"detail": "API key has no project scope."},
            ProjectScopeError,
        )

    def test_maps_quota_error(self):
        """Quota failures raise QuotaExceededError."""
        self._assert_exception(
            402,
            {"detail": "Guardrails quota exceeded"},
            QuotaExceededError,
        )

    def test_maps_guard_invocation_error(self):
        """Invocation failures raise GuardInvocationError."""
        self._assert_exception(
            502,
            {"detail": "Invocation failed: backend timeout"},
            GuardInvocationError,
        )
