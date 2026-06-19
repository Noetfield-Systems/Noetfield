"""Shared errors for public chat LLM providers."""


class ChatConfigurationError(RuntimeError):
    """Raised when no provider API key is configured on the server."""


class ChatAPIError(RuntimeError):
    """Raised when an upstream LLM API returns an error."""
