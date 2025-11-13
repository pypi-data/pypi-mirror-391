class OrchepyClientError(Exception):
    """Base exception for all Orchepy client errors."""

    def __init__(self, message: str) -> None:
        """Initialize the exception with a message."""
        super().__init__(f"OrchepyClientError: {message}")
        self.message = message


class OrchepyHTTPError(OrchepyClientError):
    """Exception raised for HTTP errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """Initialize HTTP error with message and optional status code."""
        super().__init__(message)
        self.status_code = status_code


class OrchepyNotFoundError(OrchepyHTTPError):
    """Exception raised when a resource is not found (404)."""

    def __init__(self, resource_type: str, resource_id: str) -> None:
        """Initialize not found error with resource information."""
        message = f"{resource_type} '{resource_id}' not found"
        super().__init__(message, status_code=404)
        self.resource_type = resource_type
        self.resource_id = resource_id
