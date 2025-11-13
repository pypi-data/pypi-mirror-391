"""Tests for exception classes."""

import pytest

from orchepy_client.exceptions import (
    OrchepyClientError,
    OrchepyHTTPError,
    OrchepyNotFoundError,
)


def test_orchepy_client_error() -> None:
    """Test OrchepyClientError."""
    error = OrchepyClientError("Test error")
    assert str(error) == "OrchepyClientError: Test error"
    assert error.message == "Test error"


def test_orchepy_http_error() -> None:
    """Test OrchepyHTTPError."""
    error = OrchepyHTTPError("HTTP error", status_code=500)
    assert "OrchepyClientError: HTTP error" in str(error)
    assert error.status_code == 500


def test_orchepy_http_error_without_status_code() -> None:
    """Test OrchepyHTTPError without status code."""
    error = OrchepyHTTPError("HTTP error")
    assert error.status_code is None


def test_orchepy_not_found_error() -> None:
    """Test OrchepyNotFoundError."""
    error = OrchepyNotFoundError("Case", "123")
    assert "Case '123' not found" in str(error)
    assert error.resource_type == "Case"
    assert error.resource_id == "123"
    assert error.status_code == 404
